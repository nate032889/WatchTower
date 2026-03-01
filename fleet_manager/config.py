import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_files():
    """
    Loads environment variables from .env files.
    - .env.local: For local machine-specific overrides (takes highest precedence).
    - .env: For base development/container settings.
    System environment variables will always take precedence over .env files.
    """
    # load_dotenv will not override existing system environment variables.
    # To give .env.local precedence, we load it first.
    if os.path.exists('.env.local'):
        logger.info("Loading environment from .env.local")
        load_dotenv(dotenv_path='.env.local', override=True)
    
    if os.path.exists('.env'):
        logger.info("Loading environment from .env")
        # `override=False` would be ideal, but to ensure local dev works as expected
        # when only .env is present, we let it override. The .env.local load order
        # ensures local settings are preserved if both files exist.
        load_dotenv(override=True)


class Config:
    """
    Holds all configuration for the Fleet Manager service.
    """
    def __init__(self):
        load_env_files()
        
        # --- API Endpoints ---
        # Default values are geared towards local development, but will be overridden by
        # environment variables in docker-compose.
        self.API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/api/v1/interactor/message/")
        self.API_BOT_INTEGRATIONS_URL = os.getenv("API_BOT_INTEGRATIONS_URL", "http://localhost:8000/v1/bot-integrations/")
        
        # --- Redis Configuration ---
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.PUB_SUB_CHANNEL = "bot_integrations"

def load_config() -> Config:
    """
    Loads and returns the application configuration.
    """
    return Config()
