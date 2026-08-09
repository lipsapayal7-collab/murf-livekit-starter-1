import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    tokenize,
    room_io,
    UserInputTranscribedEvent,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Change this prompt to change what your voice agent does.
# See README.md for example prompts (customer support, language tutor, receptionist).
# prompt.py

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
- Mirror the user's language and register. If they start in Hindi or mix Hindi with English (Hinglish/code-mixed), respond in natural, conversational Hinglish using Devanagari (Hindi) script (e.g. write English terms phonetically in Hindi script like 'स्कीम्स' for schemes, 'बैंक' for bank).
- Keep the tone polite, warm, and highly respectful (e.g., using 'aap').
- Ensure sentences are short and conversational, as they are spoken out loud.
- IMPORTANT: Do not use any markdown formatting, asterisks, bullet points, emojis, or special symbols in your text responses.

GUARDRAILS:
- NEVER ask the user for their PIN, OTP, password, UPI PIN, credit/debit card numbers, or full bank account numbers. If the user starts sharing this, stop them immediately and warn them.
- NEVER promise or guarantee scheme approval or loan approval. State clearly that approvals depend on meeting official criteria and are handled by the banks/government.
- ESCALATION SCRIPT: If the user asks for application tracking, account-specific issues, or claims approval status, use this response style: "Aap iski details ke liye bank branch ya official government portal visit karein. Main is scheme ke details aur eligibility criteria ke bare mein bata sakta hoon."

FIRST-TURN GREETING:
- Always start the conversation with: "नमस्ते! मैं जन सहाय हूँ। मुझे अपनी फाइनेंशियल दोस्त समझिए। मैं सरकारी फाइनेंशियल स्कीम्स और सेफ बैंकिंग से जुड़े सवालों में आपकी मदद करने के लिए यहाँ हूँ। बताइए, आज मैं आपकी कैसे मदद कर सकती हूँ?"
"""


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    # @function_tool
    # async def lookup_weather(self, context: RunContext, location: str):
    #     """Use this tool to look up current weather information in the given location.
    #
    #     If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.
    #
    #     Args:
    #         location: The location to look up weather information for (e.g. city name)
    #     """
    #
    #     logger.info(f"Looking up weather for {location}")
    #
    #     return "sunny with a temperature of 70 degrees."


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
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-3.5-flash-lite"),
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
            "kya","hai","aur","main","haan","nahi","aap",
            "namaste","shukriya","yojana","batao","batayiye",
            "samjhao","dhan","suraksha","bima","pension",
            "mein","ke","ki","se","ko","ka","jo","toh",
            "bhi","ho","kar","raha","rahi","mujhe","mera",
            "meri","hum","tum","apna","apni","karke",
            "karo","karna","tha","thi","the","ab","kab","sab"
        }

        words = set(transcript.split())
        has_hindi_words = not words.isdisjoint(hindi_keywords)

        if has_devanagari or has_hindi_words:
            session.tts.update_options(
                voice="Anisha",
                locale="hi-IN"
            )
        else:
            session.tts.update_options(
                voice="Anisha",
                locale="en-IN"
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
