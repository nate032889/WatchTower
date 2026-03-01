import asyncio
import json
import logging
import os
import sys

import redis.asyncio as redis
from dotenv import load_dotenv

from discord_client import StatelessDiscordBot

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_ENDPOINT = os.getenv("API_ENDPOINT", "http://api:8000/api/v1/interactor/message/")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PUB_SUB_CHANNEL = "bot_integrations"

# --- Bot Fleet Manager ---
class BotFleet:
    """Manages the lifecycle of multiple concurrent bot instances."""
    def __init__(self):
        self.bots = {}  # token -> asyncio.Task

    async def start_bot(self, token: str, organization_id: int):
        if token in self.bots:
            logger.warning(f"Bot for org {organization_id} with token is already running.")
            return

        logger.info(f"Starting bot for organization {organization_id}...")
        instance = StatelessDiscordBot(token, organization_id, API_ENDPOINT)
        task = asyncio.create_task(instance.start())
        self.bots[token] = task
        logger.info(f"Bot for organization {organization_id} started.")

    async def stop_bot(self, token: str):
        if token not in self.bots:
            logger.warning(f"Attempted to stop a bot that is not running.")
            return

        logger.info(f"Stopping bot with token...")
        task = self.bots.pop(token)
        task.cancel()
        logger.info(f"Bot stopped.")

# --- Redis Pub/Sub Listener ---
async def redis_listener(fleet: BotFleet):
    """Listens to Redis for commands to start or stop bots."""
    r = redis.from_url(REDIS_URL, decode_responses=True)
    pubsub = r.pubsub()
    await pubsub.subscribe(PUB_SUB_CHANNEL)
    logger.info(f"Subscribed to Redis channel: {PUB_SUB_CHANNEL}")

    while True:
        try:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=60)
            if message is None:
                continue

            data = json.loads(message["data"])
            action = data.get("action")
            token = data.get("bot_token")
            org_id = data.get("organization_id")

            if action == "start":
                await fleet.start_bot(token, org_id)
            elif action == "stop":
                await fleet.stop_bot(token)

        except asyncio.TimeoutError:
            continue
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}", exc_info=True)

# --- Main Application Loop ---
async def main():
    fleet = BotFleet()
    redis_task = asyncio.create_task(redis_listener(fleet))
    await asyncio.gather(redis_task)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Fleet manager shutting down.")
