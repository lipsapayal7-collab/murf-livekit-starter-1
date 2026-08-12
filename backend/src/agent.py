from __future__ import annotations

import logging
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
)
from livekit.plugins import deepgram, google, murf, silero

from database import init_db, create_escalation

logger = logging.getLogger("jan-sahay")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env.local")

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
AFTER REQUEST CREATION

When create_human_escalation returns successfully:
IMPORTANT:
You MUST read the exact REFERENCE_ID returned by the tool to the caller.
Do not omit it.
Do not replace it with a generic statement.
Do not invent another ID.
Say:
FOLLOW-UP METHOD

Before creating the request, ask:

"How would you prefer our team to follow up: by phone, SMS, or email?"

Accept the caller's choice.

If the caller does not want to provide a follow-up method, use:
"Not specified."

Do not ask for an email address, phone number, account number, or other
private information unless it is already safely available.

AFTER REQUEST CREATION
After the request is created, say:
"Done. Your reference ID is [REFERENCE_ID]. Our support team can review
the request and follow up by your preferred method."
Then give a short safety reminder:
"For now, don't share your OTP, PIN, password, or card details with anyone.
If you see another suspicious transaction, contact your bank through its
official customer-care channel."

Keep this short. Do not give unnecessary financial advice.
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

class JanSahay(Agent):
    def __init__(self):
        super().__init__(instructions=SYSTEM_PROMPT)

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
        logger.info("Escalation created: %s", reference_id)
        return (
            f"Request created successfully. "
            f"Reference ID: {reference_id}. "
            f"Status: Open."
        )
init_db()
server = AgentServer()
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
server.setup_fnc = prewarm
@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
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
    await session.start(
        agent=JanSahay(),
        room=ctx.room,
        room_options=room_io.RoomOptions(),
    )
    await ctx.connect()
    await session.generate_reply(
        instructions=(
            "Greet the caller naturally. Say: "
            "Hello! I'm Jan Sahay. How can I help you today?"
        )
    )
    logger.info("Jan Sahay is ready.")
if __name__ == "__main__":
    cli.run_app(server)
