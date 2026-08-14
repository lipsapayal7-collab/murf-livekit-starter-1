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
from prompt import SYSTEM_PROMPT
from specialist_agent import GovernmentSchemeSpecialist
logger = logging.getLogger("jan-sahay")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")
class JanSahay(Agent):
    def __init__(self):
        super().__init__(
            instructions=SYSTEM_PROMPT
        )
    @function_tool()
    async def handoff_to_government_scheme_specialist(
        self,
        context: RunContext,
    ):
        """
        Transfer the conversation to the Government Scheme Specialist
    for government scheme related questions.
        """
        return (
            GovernmentSchemeSpecialist(
                chat_ctx=self.chat_ctx.copy(
                    exclude_instructions=True
                )
            ),
            
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
init_db()
create_calls_table()
server = AgentServer()
def prewarm(proc: JobProcess):

    proc.userdata["vad"] = silero.VAD.load()
server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    logger.info(
        "Starting Jan Sahay session in room: %s",
        ctx.room.name
    )

  

    call_started_at = time.monotonic()

    user_spoke = False

    detected_language = "English"

    call_channel = "Browser"


    call_saved = False

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

    def save_call_result():

        nonlocal call_saved

        if call_saved:
            logger.info(
                "Call already saved. Skipping duplicate."
            )
            return

        call_saved = True

        duration = int(
            time.monotonic() - call_started_at
        )

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
                "DAY 9 CALL RECORDED"
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

            
            call_saved = False

            logger.exception(
                "Failed to save call information"
            )

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

    @session.on("close")
    def on_session_close(ev):

        logger.info(
            "Agent session closed."
        )

        save_call_result()

    await session.start(
        agent=JanSahay(),
        room=ctx.room,
        room_options=room_io.RoomOptions(),
    )

    await ctx.connect()

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


    await session.generate_reply(
        instructions=(
            "Greet the caller naturally. Say: "
            "Hello! I'm Jan Sahay. How can I help you today?"
        )
    )


    logger.info(
        "Jan Sahay is ready."
    )

if __name__ == "__main__":
    cli.run_app(server)
