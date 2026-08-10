import logging
import re
from datetime import datetime
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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

DAY 5 LIVE DATA TOOL:

- You have a tool named get_official_scheme_info.

- Call get_official_scheme_info automatically when the caller asks for current, latest, official, eligibility, premium, benefit, or factual information about PMJDY, PMSBY, or PMJJBY.

- The tool fetches information live from the official Department of Financial Services website.

- Treat the returned tool data as the source of truth for current scheme information.

- Pay attention to source_updated and fetched_at.

- Do not describe older source data as today's data.

- After a successful tool call, answer naturally in the caller's language.

- Never read JSON, field names, URLs, or raw tool output aloud.

- If the tool fails, say that live verification from the official government source is temporarily unavailable.

- Never invent or guess a current premium, eligibility requirement, benefit, or coverage amount when the live lookup fails.
- If the caller asks when the information was last updated, explicitly mention the source_updated date returned by the tool.

- If the caller asks whether the information is current, explain that the data was fetched live and mention the official source update date when available.

- Do not call information "today's update" merely because it was fetched today.
LANGUAGE:

- Always start every new call in English.
- The first greeting must always be in English.
- Example first greeting:
  "Hello! I’m Jan Sahay. I’m here to help you with financial schemes and digital banking safety. First, please tell me your user ID."

- After the caller speaks, detect their language.
- If the caller speaks English, continue in English.
- If the caller speaks Hindi or Hinglish, switch naturally to Hindi/Hinglish.
- Do not switch languages unless the caller's language clearly indicates it.
- Mirror the caller's language after the first turn.
- Keep responses short, natural, warm, and suitable for voice.

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

LIVE TOOL LIMIT:

- get_official_scheme_info currently supports only PMJDY, PMSBY, and PMJJBY.
- Do not pretend that the live tool supports APY or SSY.
- For APY or SSY, only provide information that is already explicitly available in the agent's approved knowledge.
- If the caller asks for current/latest APY or SSY figures and no live source is available, say that you cannot verify the current information live.

SCHEME REGISTRY RECOVERY:
- If the caller asks about a scheme but the scheme name is unclear or cannot be confidently identified, respond exactly:
  "I apologize, but our scheme registry is currently undergoing maintenance. However, generally for basic financial schemes, you will need standard ID proofs like a Voter ID or Driving License."
- Do not provide an answer or guess a scheme in that first response.
- If the caller asks the same or similar scheme question again, try to identify the intended scheme from the new utterance and answer it normally.
- For example:
  Caller: "Is the current PMPSY?"
  Assistant: "I apologize, but our scheme registry is currently undergoing maintenance."
  Caller: "Yes, PMPSY."
  Assistant: "Yes, if you mean PMSBY, I can help with that. The current annual premium is ₹20..."
- When the intended scheme is identified on the second attempt, use get_official_scheme_info for PMJDY, PMSBY, or PMJJBY before giving current information.
- Do not repeatedly give the maintenance message after the scheme becomes clear.
- Do not guess unrelated schemes such as PM-SYM, SSY, or APY.

FIRST-TURN GREETING:

- Always begin the first turn in English.
- Do not begin the call in Hindi.
- Say:

"Hello! I’m Jan Sahay. I’m here to help you with financial schemes and digital banking safety. First, please tell me your user ID."

- After the caller responds, detect their language and continue in that language.
- If the caller responds in Hindi or Hinglish, switch to natural Hindi/Hinglish.
- If the caller responds in English, continue in English.
- When the caller provides the user ID, immediately call lookup_caller.
"""
SCHEME_SOURCES = {
    "pmjdy": "https://www.financialservices.gov.in/pradhan-mantri-jan-dhan-yojana-pmjdy",

    "pmsby": "https://financialservices.gov.in/pmsby",

    "pmjjby": "https://www.financialservices.gov.in/pmjjby",
}


class _VisibleTextParser(HTMLParser):
    """Small stdlib-only HTML-to-text parser for official DFS pages."""

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        text = " ".join(data.split())
        if text:
            self.parts.append(text)

    def get_text(self):
        return " ".join(self.parts)


SCHEME_SOURCES = {
    "pmjdy": "https://www.financialservices.gov.in/pradhan-mantri-jan-dhan-yojana-pmjdy",
    "pmsby": "https://financialservices.gov.in/pmsby",
    "pmjjby": "https://www.financialservices.gov.in/pmjjby",
}


def _normalize_scheme_name(scheme: str) -> str:
    value = scheme.lower().strip().replace("-", "").replace(" ", "")
    aliases = {
        "pmjdy": "pmjdy",
        "pradhanmantrijandhanyojana": "pmjdy",
        "pmsby": "pmsby",
        "pradhanmantrisurakshabimayojana": "pmsby",
        "pmjjby": "pmjjby",
        "pradhanmantrijeevanjyotibimayojana": "pmjjby",
    }
    return aliases.get(value, value)


def _fetch_official_scheme_page(scheme_key: str):
    url = SCHEME_SOURCES[scheme_key]
    request = Request(
        url,
        headers={
            "User-Agent": "Jan-Sahay-Day5/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )

    with urlopen(request, timeout=8) as response:
        html = response.read().decode("utf-8", errors="replace")

    parser = _VisibleTextParser()
    parser.feed(html)
    text = parser.get_text()

    updated_match = re.search(
        r"Last Updated On:\s*(\d{2}\.\d{2}\.\d{4})",
        text,
        flags=re.IGNORECASE,
    )
    source_updated = updated_match.group(1) if updated_match else "not stated"

    if scheme_key == "pmsby":
        premium = re.search(r"Premium payable is\s+Rs\.?\s*([\d,]+)", text, re.I)
        age = re.search(r"age group of\s+(\d+)\s+to\s+(\d+)\s+years", text, re.I)
        death_cover = re.search(r"Death\s+Rs\.?\s*([\d.]+)\s*Lakh", text, re.I)
        facts = [
            f"annual premium ₹{premium.group(1)}" if premium else None,
            f"eligibility age {age.group(1)}–{age.group(2)} years" if age else None,
            f"accidental death cover ₹{death_cover.group(1)} lakh" if death_cover else None,
        ]
    elif scheme_key == "pmjjby":
        premium = re.search(r"premium payable is\s+Rs\.?\s*([\d,]+)", text, re.I)
        age = re.search(r"age group of\s+(\d+)\s+to\s+(\d+)\s+years", text, re.I)
        cover = re.search(r"Rs\.?\s*([\d.]+)\s*lakh is payable", text, re.I)
        facts = [
            f"annual premium ₹{premium.group(1)}" if premium else None,
            f"eligibility age {age.group(1)}–{age.group(2)} years" if age else None,
            f"life cover ₹{cover.group(1)} lakh" if cover else None,
        ]
    else:
        min_balance = re.search(
            r"without any minimum balance requirement", text, re.I
        )
        overdraft = re.search(
            r"overdraft facility of upto\s+₹?\s*([\d,]+)", text, re.I
        )
        facts = [
            "no minimum balance requirement" if min_balance else None,
            f"overdraft up to ₹{overdraft.group(1)}" if overdraft else None,
        ]
        if re.search(r"Free RuPay debit card", text, re.I):
            facts.append("free RuPay debit card with accident insurance cover")

    facts = [item for item in facts if item]
    if not facts:
        raise ValueError("Official page format changed; expected fields were not found.")

    scheme_names = {
        "pmjdy": "Pradhan Mantri Jan Dhan Yojana (PMJDY)",
        "pmsby": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "pmjjby": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
    }

    return {
        "success": True,
        "scheme": scheme_names[scheme_key],
        "facts": facts,
        "source": url,
        "source_updated": source_updated,
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "data_status": "LIVE — fetched from the official Department of Financial Services website.",
    }


class Assistant(Agent):

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT
        )

    @function_tool()
    async def get_official_scheme_info(
        self,
        context: RunContext,
        scheme: str,
    ):
        """
        Fetch current official information for PMJDY, PMSBY, or PMJJBY.

        Use this when the caller asks for current/latest/official scheme facts,
        eligibility, premium, or benefits. The tool fetches the Department of
        Financial Services website at call time. Never invent current figures
        if the lookup fails.
        """
        logger.info(f"SCHEME LOOKUP TOOL CALLED - scheme={scheme}")

        scheme_key = _normalize_scheme_name(scheme)

        if scheme_key not in SCHEME_SOURCES:
            return {
                "success": False,
                "error_type": "unsupported_scheme",
                "message": (
                    "Live official lookup is currently supported for PMJDY, "
                    "PMSBY, and PMJJBY."
                ),
            }

        try:
            result = _fetch_official_scheme_page(scheme_key)
            logger.info(
                "SCHEME LOOKUP SUCCESS - scheme=%s source_updated=%s",
                scheme_key,
                result.get("source_updated"),
            )
            return result

        except (HTTPError, URLError, TimeoutError) as exc:
            logger.warning("SCHEME LOOKUP NETWORK FAILURE: %s", exc)
            return {
                "success": False,
                "error_type": "network_failure",
                "message": (
    "Live verification from the official government source "
    "is temporarily unavailable. Do not guess or invent "
    "the current scheme details. Tell the caller that "
    "you cannot verify the latest information right now."
),
            }

        except Exception as exc:
            logger.exception("SCHEME LOOKUP FAILED: %s", exc)
            return {
                "success": False,
                "error_type": "source_format_changed",
                "message": (
                    "The official government page could not be safely read right now. "
                    "Do not guess current scheme figures."
                ),
            }

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
