import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_file():
    """
    Loads environment variables from the correct .env file within the fleet_manager directory.
    - .env.local: Used exclusively if it exists (for local development).
    - .env: Used as a fallback.
    """
    base_dir = Path(__file__).resolve().parent
    
    env_path = base_dir / '.env.local'
    if not env_path.exists():
        env_path = base_dir / '.env'

    if env_path.exists():
        logger.info(f"Loading environment from {env_path}")
        load_dotenv(dotenv_path=env_path)
    else:
        logger.info("No .env file found. Relying on system environment variables.")


class Config:
    """
    Holds all configuration for the Fleet Manager service.
    """
    def __init__(self):
        load_env_file()
        
        self.API_ENDPOINT = os.getenv("API_ENDPOINT", "http://localhost:8000/v1/interactor/message/")
        # Corrected to use the internal-only endpoint for syncing bots
        self.API_BOT_INTEGRATIONS_URL = os.getenv("API_BOT_INTEGRATIONS_URL", "http://localhost:8000/v1/internal/bot-integrations/")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.PUB_SUB_CHANNEL = "bot_integrations"

def load_config() -> Config:
    """
    Loads and returns the application configuration.
    """
    return Config()
