import os
import sys
import discord
import requests
import logging
from dotenv import load_dotenv

from logging_config import setup_logging
from data.database import get_db
from data.history_repository import HistoryRepository
from service.conversation_service import ConversationService

# --- Setup ---
setup_logging()
load_dotenv()
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the Discord bot.
    """
    # --- Configuration ---
    token = os.getenv('DISCORD_BOT_TOKEN')
    api_endpoint = os.getenv('WATCHTOWER_API_ENDPOINT')
    message_limit = int(os.getenv('DISCORD_MESSAGE_LIMIT', 2000))

    if not token or not api_endpoint:
        logger.critical('DISCORD_BOT_TOKEN and WATCHTOWER_API_ENDPOINT must be set in .env')
        sys.exit(1)

    # --- Discord Client Setup ---
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    # --- Helper for Sending Messages ---
    async def send_in_chunks(channel, text: str):
        """
        Sends a long string of text in chunks, respecting the Discord message limit.
        :param channel: The Discord channel to send the message to.
        :param text: The text to send.
        """
        ai_chunks = text.split('[SPLIT]')
        for ai_chunk in ai_chunks:
            if not ai_chunk.strip():
                continue
            remaining_text = ai_chunk.strip()
            while len(remaining_text) > 0:
                if len(remaining_text) <= message_limit:
                    await channel.send(remaining_text)
                    break
                split_at = remaining_text.rfind('\\n', 0, message_limit)
                if split_at == -1:
                    split_at = message_limit
                chunk_to_send = remaining_text[:split_at]
                remaining_text = remaining_text[split_at:].lstrip()
                if chunk_to_send:
                    await channel.send(chunk_to_send)

    # --- Bot Events ---
    @client.event
    async def on_ready():
        """
        Event handler for when the bot successfully logs in.
        """
        HistoryRepository.create_tables()
        logger.info(f'Logged in as {client.user}')

    @client.event
    async def on_message(message: discord.Message):
        """
        Event handler for when a message is received.
        :param message: The Discord message object.
        """
        if message.author == client.user or not client.user.mentioned_in(message):
            return

        db_session = next(get_db())
        try:
            repo = HistoryRepository(db_session)
            service = ConversationService(repo)
            
            prompt = message.content.replace(f'<@!{client.user.id}>', '').strip()
            is_thread = isinstance(message.channel, discord.Thread)
            channel_id = message.channel.parent_id if is_thread else message.channel.id
            
            history_key, history_dto = service.get_history_for_message(channel_id, message.author.id, is_thread)
            logger.info(f"Processing prompt for key '{history_key}' with history length {len(history_dto)}")

            history_for_api = [{"role": msg.role, "parts": [msg.content]} for msg in history_dto]

            payload = {'prompt': prompt, 'history': history_for_api}
            response = requests.post(api_endpoint, json=payload)
            response.raise_for_status()
            full_response = response.json().get('response', 'Sorry, I had trouble getting a response.')

            service.add_turn_to_history(history_key, prompt, full_response)
            service.check_and_summarize(history_key)

            await send_in_chunks(message.channel, full_response)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling WatchTower API: {e}")
            await message.channel.send("Sorry, I couldn't connect to the WatchTower service.")
        except Exception as e:
            logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
            await message.channel.send("An unexpected error occurred. Please check the logs.")
        finally:
            db_session.close()

    client.run(token)

if __name__ == '__main__':
    main()
