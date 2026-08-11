import os
import asyncio
import logging
import sys
import time

from dotenv import load_dotenv
from livekit import api


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("outbound_call")


async def main():
    load_dotenv(".env.local")

    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")

    if not livekit_url or not livekit_api_key or not livekit_api_secret:
        logger.error("LiveKit credentials are missing from .env.local")
        sys.exit(1)

    # SIP destination
    if len(sys.argv) > 1:
        target_number = sys.argv[1]
    else:
        target_number = os.getenv("LINPHONE_SIP_URI")

    if not target_number:
        logger.error("LINPHONE_SIP_URI is missing from .env.local")
        sys.exit(1)

    # LiveKit SIP expects the destination.
    # For a Linphone SIP account, keep the SIP URI.
    if target_number.startswith("sip:"):
        target_number = target_number[4:]

    if "@" in target_number:
     target_number = target_number.split("@")[0]

    sip_trunk_id = os.getenv("LIVEKIT_SIP_TRUNK_ID")

    if not sip_trunk_id:
        logger.error("LIVEKIT_SIP_TRUNK_ID is missing from .env.local")
        sys.exit(1)

    room_name = f"jan-sahay-{int(time.time())}"

    logger.info("Connecting to LiveKit...")
    logger.info("Room: %s", room_name)
    logger.info("SIP target: %s", target_number)
    logger.info("SIP trunk: %s", sip_trunk_id)

    lk_api = api.LiveKitAPI(
        url=livekit_url,
        api_key=livekit_api_key,
        api_secret=livekit_api_secret,
    )

    try:
        # Start Jan Sahay agent in this room first.
        logger.info("Creating agent dispatch...")

        dispatch = await lk_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="my-agent",
                room=room_name,
            )
        )

        logger.info("Agent dispatch created: %s", dispatch.id)

        # Dial the Linphone SIP account.
        logger.info("Calling SIP participant...")

        participant = await lk_api.sip.create_sip_participant(
            api.CreateSIPParticipantRequest(
                room_name=room_name,
                sip_call_to=target_number,
                sip_trunk_id=sip_trunk_id,
                participant_identity="sip_user_linphone",
                participant_name="Lipsa",
                wait_until_answered=True,
            )
        )

        logger.info("Outbound SIP call connected.")
        logger.info("Participant: %s", participant)

        print()
        print("=" * 60)
        print("       JAN SAHAY — DAY 6 OUTBOUND CALL")
        print("=" * 60)
        print(f"Room      : {room_name}")
        print(f"SIP Target: {target_number}")
        print(f"Participant: sip_user_linphone")
        print("=" * 60)
        print()
        print("📞 Call connected. Jan Sahay should speak now.")

    except Exception as e:
        logger.exception("Outbound SIP call failed: %s", e)

    finally:
        await lk_api.aclose()


if __name__ == "__main__":
    asyncio.run(main())
