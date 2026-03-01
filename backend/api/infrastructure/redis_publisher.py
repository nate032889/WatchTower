import redis
import os
import json
import logging

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
PUB_SUB_CHANNEL = "bot_integrations"

try:
    # Use a blocking client for simple fire-and-forget publishing
    redis_client = redis.from_url(REDIS_URL)
except Exception as e:
    logger.error(f"Could not connect to Redis for publishing: {e}")
    redis_client = None

def publish_bot_command(action: str, bot_token: str, organization_id: int):
    """
    Publishes a command to the bot integrations channel.
    :param action: The action to perform ('start' or 'stop').
    :param bot_token: The token of the bot to command.
    :param organization_id: The ID of the organization the bot belongs to.
    """
    if not redis_client:
        logger.error("Redis client not available. Cannot publish bot command.")
        return

    try:
        message = {
            "action": action,
            "bot_token": bot_token,
            "organization_id": organization_id,
        }
        redis_client.publish(PUB_SUB_CHANNEL, json.dumps(message))
        logger.info(f"Published '{action}' command for org {organization_id} to Redis.")
    except Exception as e:
        logger.error(f"Failed to publish bot command to Redis: {e}")
