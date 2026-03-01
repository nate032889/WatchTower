import asyncio
import logging
from typing import Tuple, Dict, Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class WatchTowerApiClient:
    """
    An infrastructure client for communicating with the main WatchTower backend API.
    Isolates all aiohttp logic.
    """

    def __init__(self, api_endpoint: str):
        """
        Initializes the client with the target API endpoint.
        :param api_endpoint: The base URL for the WatchTower API.
        """
        self.api_endpoint = api_endpoint

    async def send_message(self, payload: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        """
        Sends a message payload to the WatchTower API's interactor endpoint.

        :param payload: The dictionary containing the message data.
        :return: A tuple of (response_dict, None) on success, or (None, Exception) on failure.
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=120)) as session:
                async with session.post(self.api_endpoint, json=payload) as response:
                    response.raise_for_status()  # Raises ClientResponseError for 4xx/5xx statuses
                    response_json = await response.json()
                    return response_json, None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"API call failed: {e}")
            return None, e
