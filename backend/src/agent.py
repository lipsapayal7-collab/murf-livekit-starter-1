from __future__ import annotations

import logging
import time
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc

from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    UserInputTranscribedEvent,
    cli,
    function_tool,
    room_io,
)

from livekit.plugins import deepgram, google, murf, silero

from database import (
    init_db,
    create_calls_table,
    create_escalation,
    save_call,
)


logger = logging.getLogger("jan-sahay")


# ============================================================
# PROJECT SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env.local")


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are Jan Sahay, a friendly financial services AI assistant.

Your job is to answer simple financial questions, but you must not try
to solve every problem yourself.

DAY 7 HUMAN HELP

Escalate only in these two situations:

1. Possible fraud or an unauthorized transaction.
2. A decision that you are not authorized or able to make.

Examples:

- "I don't recognize this transaction."
- "Someone may have used my account."
- "I think this is fraud."
- "Can you approve my application?"
- "Can you approve my loan?"
- "Can you make this decision?"

NORMAL QUESTIONS

If you can answer the question yourself, answer normally.

Do NOT create an escalation for normal questions.

BEFORE CREATING A REQUEST

Never create an escalation immediately.

Say:

"This may need further review. I can send a short summary of the issue,
what I checked, the urgency, and your preferred follow-up. I won't share
sensitive information. Would you like me to send this to our support team?"

Only call create_human_escalation after the caller clearly says YES.

If the caller says NO:

- Do not call the tool.
- Say: "No problem. I won't create a request."

If the answer is unclear, ask again.

ESCALATION SUMMARY

Send only:

- Who needs help
- What happened
- What was already checked
- Urgency
- Language
- Preferred follow-up method

Never include:

- Passwords
- OTPs
- PINs
- CVVs
- Card numbers
- Bank account numbers
- Aadhaar numbers
- PAN numbers

If the caller gives sensitive information, do not repeat or store it.

FOLLOW-UP METHOD

Before creating the request, ask:

"How would you prefer our team to follow up: by phone, SMS, or email?"

Accept the caller's choice.

If the caller does not want to provide a follow-up method, use:

"Not specified."

Do not ask for an email address, phone number, account number, or other
private information unless it is already safely available.

AFTER REQUEST CREATION

When create_human_escalation returns successfully:

IMPORTANT:

You MUST read the exact REFERENCE_ID returned by the tool to the caller.

Do not omit it.

Do not replace it with a generic statement.

Do not invent another ID.

After the request is created, say:

"Done. Your reference ID is [REFERENCE_ID]. Our support team can review
the request and follow up by your preferred method."

Then give a short safety reminder:

"For now, don't share your OTP, PIN, password, or card details with anyone.
If you see another suspicious transaction, contact your bank through its
official customer-care channel."

Keep this short.

Do not give unnecessary financial advice.

Do not say "human specialist".

Do not promise an immediate response.

Keep the response short.

LANGUAGE

Start in simple English.

Keep responses short and natural for a voice conversation.

ENDING

If the caller says goodbye, stop, or asks to end the conversation,
respond politely and end the conversation.
"""


# ============================================================
# JAN SAHAY AGENT
# ============================================================

class JanSahay(Agent):

    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT
        )

    @function_tool()
    async def create_human_escalation(
        self,
        context: RunContext,
        who_needs_help: str,
        what_happened: str,
        what_was_checked: str,
        urgency: str,
        language: str,
        preferred_followup: str,
    ) -> str:
        """Create a human support request after caller consent."""

        reference_id = create_escalation(
            who_needs_help=who_needs_help,
            what_happened=what_happened,
            what_was_checked=what_was_checked,
            urgency=urgency,
            language=language,
            preferred_followup=preferred_followup,
        )

        logger.info(
            "Escalation created: %s",
            reference_id
        )

        return (
            f"Request created successfully. "
            f"Reference ID: {reference_id}. "
            f"Status: Open."
        )


# ============================================================
# DATABASE
# ============================================================

init_db()

# Make sure calls table exists
create_calls_table()


# ============================================================
# LIVEKIT SERVER
# ============================================================

server = AgentServer()


# ============================================================
# PREWARM
# ============================================================

def prewarm(proc: JobProcess):

    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


# ============================================================
# RTC SESSION
# ============================================================

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    logger.info(
        "Starting Jan Sahay session in room: %s",
        ctx.room.name
    )

    # ========================================================
    # CALL TRACKING VARIABLES
    # ========================================================

    call_started_at = time.monotonic()

    user_spoke = False

    detected_language = "English"

    call_channel = "Browser"

    # Prevent duplicate database entries
    call_saved = False


    # ========================================================
    # AGENT SESSION
    # ========================================================

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
            locale="en-IN",
            style="Conversation",
        ),

        vad=ctx.proc.userdata["vad"],

        preemptive_generation=True,
    )


    # ========================================================
    # LANGUAGE DETECTION
    # ========================================================

    @session.on("user_input_transcribed")
    def on_user_input_transcribed(
        ev: UserInputTranscribedEvent
    ):

        nonlocal user_spoke
        nonlocal detected_language

        transcript = ev.transcript.strip().lower()

        if not transcript:
            return

        # Caller actually spoke
        user_spoke = True

        # ----------------------------------------------------
        # Hindi detection
        # ----------------------------------------------------

        has_devanagari = any(
            0x0900 <= ord(char) <= 0x097F
            for char in transcript
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

        words = set(
            transcript.split()
        )

        has_hindi_words = not words.isdisjoint(
            hindi_keywords
        )

        # ----------------------------------------------------
        # Update language
        # ----------------------------------------------------

        if has_devanagari or has_hindi_words:

            detected_language = "Hindi"

            session.tts.update_options(
                voice="Anisha",
                locale="hi-IN"
            )

        else:

            detected_language = "English"

            session.tts.update_options(
                voice="Anisha",
                locale="en-IN"
            )

        logger.info(
            "Detected language: %s",
            detected_language
        )


    # ========================================================
    # SAVE CALL FUNCTION
    # ========================================================

    def save_call_result():

        nonlocal call_saved

        # ----------------------------------------------------
        # Prevent duplicate records
        # ----------------------------------------------------

        if call_saved:
            logger.info(
                "Call already saved. Skipping duplicate."
            )
            return

        call_saved = True

        # ----------------------------------------------------
        # Calculate duration
        # ----------------------------------------------------

        duration = int(
            time.monotonic() - call_started_at
        )

        # ----------------------------------------------------
        # Determine outcome
        # ----------------------------------------------------

        if not user_spoke:

            outcome = "Failed"

            failure_reason = "Incomplete Task"

            outcome_result = (
                "Caller connected but did not provide input"
            )

        else:

            outcome = "Success"

            failure_reason = None

            outcome_result = (
                "Conversation Completed"
            )

        # ----------------------------------------------------
        # Save into database
        # ----------------------------------------------------

        try:

            save_call(
                user_id="Lipsa",
                channel=call_channel,
                language=detected_language,
                duration=duration,
                outcome=outcome,
                failure_reason=failure_reason,
                outcome_result=outcome_result,
            )

            logger.info(
                "=========================================="
            )

            logger.info(
                "DAY 8 CALL RECORDED"
            )

            logger.info(
                "Channel: %s",
                call_channel
            )

            logger.info(
                "Language: %s",
                detected_language
            )

            logger.info(
                "Duration: %s seconds",
                duration
            )

            logger.info(
                "Outcome: %s",
                outcome
            )

            logger.info(
                "=========================================="
            )

        except Exception:

            # If database saving fails,
            # allow another event to try again.
            call_saved = False

            logger.exception(
                "Failed to save call information"
            )


    # ========================================================
    # CALLER DISCONNECT EVENT
    # ========================================================

    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(
        participant: rtc.RemoteParticipant
    ):

        logger.info(
            "Participant disconnected: %s",
            participant.identity
        )

        logger.info(
            "Saving call because participant disconnected..."
        )

        save_call_result()


    # ========================================================
    # SESSION CLOSE BACKUP
    # ========================================================

    @session.on("close")
    def on_session_close(ev):

        logger.info(
            "Agent session closed."
        )

        save_call_result()


    # ========================================================
    # START SESSION
    # ========================================================

    await session.start(
        agent=JanSahay(),
        room=ctx.room,
        room_options=room_io.RoomOptions(),
    )


    # ========================================================
    # CONNECT TO LIVEKIT ROOM
    # ========================================================

    await ctx.connect()


    # ========================================================
    # DETECT ACTUAL CALL CHANNEL
    # ========================================================

    try:

        for participant in ctx.room.remote_participants.values():

            if (
                participant.kind
                == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
            ):

                call_channel = "SIP"

                break

    except Exception:

        logger.warning(
            "Could not determine call channel. "
            "Using Browser as default."
        )


    logger.info(
        "Call channel detected: %s",
        call_channel
    )


    # ========================================================
    # GREETING
    # ========================================================

    await session.generate_reply(
        instructions=(
            "Greet the caller naturally. Say: "
            "Hello! I'm Jan Sahay. How can I help you today?"
        )
    )


    logger.info(
        "Jan Sahay is ready."
    )


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":
    cli.run_app(server)
