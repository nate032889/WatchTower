import asyncio
import json
import logging
from typing import Dict
import aiohttp
import redis.asyncio as redis
from delivery.discord_bot import StatelessDiscordBot
from infrastructure.api_client import WatchTowerApiClient
from service.message_service import MessageService
from config import load_config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
config = load_config()


class BotFleet:
    """
    Manages the lifecycle of multiple concurrent bot instances.
    """

    def __init__(self):
        self.bots: Dict[str, asyncio.Task] = {}  # token -> asyncio.Task

    async def start_bot(self, token: str, organization_id: int):
        """
        Instantiates all layers and starts a new bot instance as a concurrent task.
        """
        if not token:
            logger.error(f"Attempted to start bot for org {organization_id} with an empty token.")
            return
        
        if token in self.bots:
            logger.warning(f"Bot for org {organization_id} is already running.")
            return

        logger.info(f"Starting bot for organization {organization_id}...")
        api_client = WatchTowerApiClient(api_endpoint=config.API_ENDPOINT)
        message_service = MessageService(api_client=api_client)
        bot = StatelessDiscordBot(
            token=token,
            organization_id=organization_id,
            message_service=message_service
        )
        task = asyncio.create_task(bot.start_bot())
        self.bots[token] = task
        logger.info(f"Bot for organization {organization_id} started successfully.")

    async def stop_bot(self, token: str):
        """
        Stops and removes a running bot instance.
        """
        if token not in self.bots:
            logger.warning(f"Attempted to stop a bot that is not running (token: {token[:5]}...).")
            return

        logger.info(f"Stopping bot (token: {token[:5]}...).")
        task = self.bots.pop(token)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Bot task successfully cancelled.")


async def sync_initial_state(fleet: BotFleet):
    """
    On startup, fetches all active bots from the API and starts them.
    """
    logger.info("Performing initial state sync...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(config.API_BOT_INTEGRATIONS_URL) as response:
                response.raise_for_status()
                integrations = await response.json()
                logger.info(f"Found {len(integrations)} active integrations to start.")
                for integration in integrations:
                    await fleet.start_bot(
                        token=integration.get("bot_token"),
                        organization_id=integration.get("organization")
                    )
    except aiohttp.ClientError as e:
        logger.error(f"Could not perform initial sync with API: {e}. Fleet may be out of sync.")


async def redis_listener(fleet: BotFleet):
    """
    Listens to Redis for commands to start or stop bots.
    """
    r = redis.from_url(config.REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(config.PUB_SUB_CHANNEL)
    logger.info(f"Subscribed to Redis channel: '{config.PUB_SUB_CHANNEL}'")

    while True:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=60)
            if message is None:
                continue

            logger.info(f"Received command from Redis: {message['data']}")
            data = json.loads(message["data"])
            action = data.get("action")
            token = data.get("bot_token")
            org_id = data.get("organization_id")

            if action == "start" and token and org_id:
                await fleet.start_bot(token, org_id)
            elif action == "stop" and token:
                await fleet.stop_bot(token)

        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}", exc_info=True)


async def main():
    """
    The main entrypoint for the Fleet Manager service.
    """
    fleet = BotFleet()
    await sync_initial_state(fleet)
    redis_task = asyncio.create_task(redis_listener(fleet))
    await asyncio.gather(redis_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Fleet manager shutting down.")
