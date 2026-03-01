import logging
from typing import Tuple, Optional, List

from infrastructure.api_client import WatchTowerApiClient

logger = logging.getLogger(__name__)


class MessageService:
    """
    The service layer for processing messages. It contains the business logic
    and orchestrates calls to the infrastructure layer.
    """

    def __init__(self, api_client: WatchTowerApiClient):
        """
        Initializes the service with a WatchTowerApiClient instance.
        :param api_client: The client for communicating with the backend API.
        """
        self.api_client = api_client

    async def process_discord_message(
        self,
        organization_id: int,
        channel_id: str,
        author_id: str,
        content: str,
        attachment_urls: List[str],
    ) -> Tuple[Optional[str], Optional[Exception]]:
        """
        Constructs a payload and sends it to the WatchTower API via the infrastructure client.

        :param organization_id: The ID of the organization the bot belongs to.
        :param channel_id: The ID of the Discord channel the message came from.
        :param author_id: The ID of the user who sent the message.
        :param content: The text content of the message.
        :param attachment_urls: A list of URLs for any attachments.
        :return: A tuple of (response_string, None) on success, or (error_message_for_user, Exception) on failure.
        """
        # 1. Construct the standard payload for the WatchTower API
        payload = {
            "platform": "discord",
            "organization_id": organization_id,
            "channel_id": channel_id,
            "user_id": author_id,
            "content": content,
            "attachment_urls": attachment_urls,
        }

        # 2. Pass the payload to the infrastructure client
        response_data, err = await self.api_client.send_message(payload)

        # 3. Unpack the Go-style tuple and handle the result
        if err:
            logger.error(f"Error received from API client: {err}")
            # Return a user-facing error message and the actual exception
            return "Sorry, I couldn't connect to the WatchTower engine.", err

        # 4. On success, extract the response string and return it
        response_string = response_data.get("response", "Error: The API returned an empty response.")
        return response_string, None
