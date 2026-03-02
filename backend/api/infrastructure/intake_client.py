import logging
import os
from typing import Tuple, Dict, Any, Optional

import requests

logger = logging.getLogger(__name__)

# The base URL for the Go intake service.
# Corrected to match the Go service's route structure (no /api prefix).
INTAKE_SERVICE_URL = os.getenv("INTAKE_SERVICE_URL", "http://intake-service:3000/v1/intake")


class IntakeServiceClient:
    """
    A client for communicating with the Go-based intake_service.
    This class isolates all HTTP logic for processing attachments.
    """

    @staticmethod
    def process_attachment(url: str) -> Tuple[Optional[Dict[str, Any]], Optional[Exception]]:
        """
        Downloads a file from a URL and sends it to the intake_service for processing.

        :param url: The public URL of the file to process.
        :return: A tuple of (response_dict, None) on success, or (None, Exception) on failure.
        """
        try:
            # 1. Download the file from the source URL into memory
            logger.info(f"Downloading attachment from: {url}")
            file_response = requests.get(url, stream=True, timeout=15)
            file_response.raise_for_status()
            file_content = file_response.content
            # Sanitize filename to remove query parameters
            filename = url.split('/')[-1].split('?')[0]

            # 2. POST the file as multipart/form-data to the intake_service
            logger.info(f"Forwarding '{filename}' to intake service at {INTAKE_SERVICE_URL}")
            files = {'file': (filename, file_content)}
            intake_response = requests.post(INTAKE_SERVICE_URL, files=files, timeout=120)
            intake_response.raise_for_status()

            # 3. On success, return the JSON response and no error
            return intake_response.json(), None

        except requests.exceptions.RequestException as e:
            # 4. On any network or HTTP error, return None and the exception
            logger.error(f"Failed to process attachment at {url}. Error: {e}")
            return None, e
