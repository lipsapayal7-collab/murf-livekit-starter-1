import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    function_tool,
    cli,
    inference,
    tokenize,
    room_io,
    UserInputTranscribedEvent,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from database import init_db, lookup_user, save_user

logger = logging.getLogger("agent")

load_dotenv(".env.local")


SYSTEM_PROMPT = """
IDENTITY:

- Name: Jan Sahay (जन सहाय)
- Backstory: You are a friendly, warm, and highly knowledgeable digital assistant representing the National Financial Literacy Council (NFLC) of India.
- Creator / Organization: If asked who built or created you ("kisne banaya hai"), state that you were made by Miss Lipsa Ji.
- Role: Your purpose is to educate citizens, make financial literacy accessible, and promote safe digital banking habits across India.

OBJECTIVES:

- Provide clear and correct information about Indian government financial schemes (such as PMJDY, PMSBY, PMJJBY, APY, SSY).
- Confirm that the user understands the key eligibility criteria or next steps to apply for their schemes of interest.
- Actively raise awareness about digital banking safety, emphasizing how to protect oneself from online fraud.

KNOWLEDGE:

- Schemes: Pradhan Mantri Jan Dhan Yojana (PMJDY), Pradhan Mantri Suraksha Bima Yojana (PMSBY), Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY), Atal Pension Yojana (APY), and Sukanya Samriddhi Yojana (SSY).
- Digital Payments: UPI, mobile banking apps, ATMs, and safe transactions.
- Boundaries: You do not have access to individual user bank account records, cannot check application statuses, and cannot process applications directly.

LANGUAGE:

- Mirror the user's language and register.
- If the user speaks Hindi or Hinglish, respond naturally in Hindi/Hinglish.
- If the user clearly prefers English, respond in English.
- Keep the tone polite, warm, and respectful.
- Keep sentences short and conversational because responses are spoken aloud.
- Do not use markdown formatting, bullet points, emojis, or special symbols in spoken responses.

GUARDRAILS:

- NEVER ask the user for their PIN, OTP, password, UPI PIN, credit/debit card numbers, or full bank account numbers.
- If the user starts sharing sensitive banking information, stop them and warn them.
- NEVER promise or guarantee scheme approval or loan approval.
- If the user asks for application tracking, account-specific issues, or approval status, say:
  "Aap iski details ke liye bank branch ya official government portal visit karein. Main is scheme ke details aur eligibility criteria ke bare mein bata sakta hoon."

MEMORY AND CONSENT:

- You have two memory tools: lookup_caller and save_caller.
- These tools are the ONLY way you access caller memory.
- Do not invent or assume caller information.

USER ID LOOKUP:

- When the caller provides a user ID, ALWAYS call lookup_caller before asking for their name, preferred language, scheme, or other personal information.
- Do not guess whether the caller is new or returning.
- If lookup_caller returns found=true, use the returned saved information.
- If lookup_caller returns found=false, treat the caller as new.

NEW CALLER:

- If no profile is found, ask for the caller's name.
- Ask for their preferred language.
- Ask which financial scheme they are interested in.
- Ask only relevant general eligibility questions.
- After collecting useful information that should be remembered, proactively ask for permission to save it.
- The caller must not have to ask you to save their information.

MANDATORY CONSENT:

- NEVER call save_caller without explicit permission.
- Before saving, ask:
  "I can remember your name, preferred language, and the scheme we discussed for your next call. Is it okay if I save this information?"
- Wait for a clear yes.
- If the caller says yes, call save_caller.
- If the caller says no, do not call save_caller.
- If the answer is unclear, ask for clear permission.
- Silence is not permission.

RETURNING CALLER:

- If lookup_caller finds the caller, greet them by their saved name.
- Use their saved language preference.
- Continue from the saved scheme or previous interaction.
- Do not ask again for information that is already available.
- Only mention information that was actually returned by lookup_caller.

UPDATING MEMORY:

- If a returning caller gives new information that should be remembered, explain what you want to remember and ask for permission before calling save_caller again.

PRIVACY:

- Never store Aadhaar numbers.
- Never store PAN numbers.
- Never store bank account numbers.
- Never store debit or credit card numbers.
- Never store OTPs.
- Never store PINs.
- Never store passwords.
- Never ask for these details.

FIRST-TURN GREETING:

- Start warmly and briefly.
- Ask for the caller's user ID.
- Once the caller gives the ID, call lookup_caller immediately.
- If found, greet them by their saved name and continue from their previous interaction.
- If not found, continue as a new caller.
"""


class Assistant(Agent):

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT
        )

    @function_tool()
    async def lookup_caller(
        self,
        context: RunContext,
        user_id: str,
    ):
        """
        Look up an existing caller in the persistent database.

        Always use this tool when the caller provides a user ID.
        Use the result to determine whether the caller is new or returning.
        """

        logger.info(f"LOOKUP TOOL CALLED - raw user_id={user_id}")

        # Convert spoken number words into digits
        number_words = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
        }

        normalized_id = user_id.lower().strip()

        for word, digit in number_words.items():
            normalized_id = normalized_id.replace(word, digit)

        normalized_id = normalized_id.replace(" ", "")

        logger.info(
            f"LOOKUP USING NORMALIZED ID={normalized_id}"
        )

        user = lookup_user(normalized_id)

        if user is None:
            logger.info(
                f"NO CALLER FOUND - user_id={normalized_id}"
            )

            return {
                "found": False,
                "message": "No saved profile was found for this user ID.",
            }

        logger.info(
            f"CALLER FOUND - user_id={normalized_id}, "
            f"name={user.get('name', 'Unknown')}"
        )

        return {
            "found": True,
            "user": user,
        }

    @function_tool()
    async def save_caller(
        self,
        context: RunContext,
        user_id: str,
        name: str,
        language_preference: str,
        schemes_checked: str,
        eligibility_answers: str,
    ):
        """
        Save safe caller information to the persistent database.

        Only call this tool after the caller has clearly and explicitly
        given permission to save their information.

        Never save Aadhaar, PAN, bank account numbers, card numbers,
        OTPs, PINs, passwords, or banking credentials.
        """

        logger.info(f"SAVE TOOL CALLED - user_id={user_id}")

        facts = {
            "schemes_checked": schemes_checked,
            "eligibility_answers": eligibility_answers,
        }

        save_user(
            user_id=user_id,
            name=name,
            language_preference=language_preference,
            facts=facts,
        )

        logger.info(f"CALLER SAVED - user_id={user_id}")

        return {
            "success": True,
            "message": "Caller information saved successfully.",
        }


init_db()

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    session = AgentSession(
        stt=deepgram.STT(
            model="nova-3",
            language="multi",
        ),
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),
        tts=murf.TTS(
            voice="Anisha",
            locale="hi-IN",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(ev: UserInputTranscribedEvent):

        transcript = ev.transcript.strip().lower()

        if not transcript:
            return

        has_devanagari = any(
            0x0900 <= ord(c) <= 0x097F
            for c in transcript
        )

        hindi_keywords = {
            "kya",
            "hai",
            "aur",
            "main",
            "haan",
            "nahi",
            "aap",
            "namaste",
            "shukriya",
            "yojana",
            "batao",
            "batayiye",
            "samjhao",
            "dhan",
            "suraksha",
            "bima",
            "pension",
            "mein",
            "ke",
            "ki",
            "se",
            "ko",
            "ka",
            "jo",
            "toh",
            "bhi",
            "ho",
            "kar",
            "raha",
            "rahi",
            "mujhe",
            "mera",
            "meri",
            "hum",
            "tum",
            "apna",
            "apni",
            "karke",
            "karo",
            "karna",
            "tha",
            "thi",
            "the",
            "ab",
            "kab",
            "sab",
        }

        words = set(transcript.split())
        has_hindi_words = not words.isdisjoint(hindi_keywords)

        if has_devanagari or has_hindi_words:
            session.tts.update_options(
                voice="Anisha",
                locale="hi-IN",
            )
        else:
            session.tts.update_options(
                voice="Anisha",
                locale="en-IN",
            )
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )
    await ctx.connect()
if __name__ == "__main__":
    cli.run_app(server)
