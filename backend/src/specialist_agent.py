from __future__ import annotations
from livekit.agents import Agent
from prompt import GOVERNMENT_SCHEME_SPECIALIST_PROMPT
class GovernmentSchemeSpecialist(Agent):
    def __init__(self, chat_ctx=None):
        super().__init__(
            instructions=GOVERNMENT_SCHEME_SPECIALIST_PROMPT,
            chat_ctx=chat_ctx,
        )
    async def on_enter(self) -> None:
        await self.session.generate_reply(
            instructions=(
                "Say exactly this sentence and nothing else: "
                "Hello! I’m your Government Scheme Specialist. "
                "How can I help you today?"
            )
        )
