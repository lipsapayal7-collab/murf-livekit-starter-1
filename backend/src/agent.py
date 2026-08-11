from __future__ import annotations

import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero

from database import init_db

logger = logging.getLogger("jan-sahay")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")

AGENT_NAME = "my-agent"
ROOM_PREFIX = "jan-sahay-"


SYSTEM_PROMPT = """
You are Jan Sahay, a friendly AI assistant making an outbound phone call.

This is a Day 6 outbound call about a government financial scheme.

CALL FLOW:

1. Tell the customer which government scheme they are eligible for.
2. Clearly state the exact application deadline date.
3. Ask:
   "Would you like to apply for this scheme?
   Please say yes if you want to apply, or no if you want to end the call."

IMPORTANT:
- YES means the customer wants to apply.
- NO means the customer wants to end the call.

If the customer says YES:
- Say that you can provide general information about the application.
- Continue helping them naturally.
- Do not claim that the application has been submitted or approved.

If the customer says NO:
- Say:
  "No problem. Thank you for your time. Have a great day. Goodbye."
- End the conversation.

If the customer says "I want to end the call", "goodbye", "stop",
or otherwise clearly asks to end the call:
- Say:
  "Of course. Thank you for your time. Have a great day. Goodbye."
- End the conversation.

LANGUAGE:
- Speak in clear, simple English.
- Keep responses short and natural for a phone call.
- Clearly pronounce the scheme name and deadline date.

SAFETY:
- Never ask for Aadhaar, PAN, OTP, PIN, password, CVV,
  card number, or full bank account number.
- Never claim an application is submitted or approved.
"""


def get_job_metadata(ctx: JobContext) -> dict:
    metadata = getattr(ctx.job, "metadata", None)

    if not metadata:
        return {}

    try:
        return json.loads(metadata)
    except (json.JSONDecodeError, TypeError):
        return {}


def is_outbound_room(room_name: str) -> bool:
    return room_name.startswith(ROOM_PREFIX)


class JanSahay(Agent):
    def __init__(self, instructions: str = SYSTEM_PROMPT):
        super().__init__(instructions=instructions)


init_db()

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name=AGENT_NAME)
async def my_agent(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

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
        ),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=JanSahay(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant
                    and params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()

    if not is_outbound_room(ctx.room.name):
        return

    metadata = get_job_metadata(ctx)

    customer_name = metadata.get("customer_name", "there")
    scheme_name = metadata.get("scheme_name", "Pradhan Mantri Suraksha Bima Yojana ")
    deadline = metadata.get(
        "application_deadline",
        "August 15, 2026",
    )
    opening_line = (
        f"Hello, this is Jan Sahay. "
        f"I'm calling to inform you that you are eligible "
        f"for the {scheme_name} "
        f"The application deadline is {deadline}. "
        f"Would you like to apply for this scheme? "
        f"Please say yes if you want to apply, or no if you want stop these call."
)
    participant = None
    for attempt in range(30):
        participants = list(ctx.room.remote_participants.values())
        participant = next(
            (
                p
                for p in participants
                if p.kind
                == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
            ),
            None,
        )
        logger.info(
            "Waiting for SIP participant (%d/30). Found: %s",
            attempt + 1,
            [p.identity for p in participants],
        )
        if participant:
            break
        await asyncio.sleep(1)
    if participant is None:
        logger.error("SIP phone participant was not found.")
        return
    logger.info(
        "Phone connected: %s",
        participant.identity,
    )
    session.room_io.set_participant(participant.identity)
    await asyncio.sleep(0.5)
    logger.info("Speaking Day 6 greeting...")
    handle = session.say(
        opening_line,
        allow_interruptions=False,
    )
    await asyncio.wait_for(
        handle.wait_for_playout(),
        timeout=60,
    )
    logger.info(
        "Day 6 greeting completed for %s.",
        customer_name,
    )
if __name__ == "__main__":
    cli.run_app(server)
