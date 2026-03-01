import logging
import os
import discord
from service.message_service import MessageService

logger = logging.getLogger(__name__)


class StatelessDiscordBot(discord.Client):
    """
    The Delivery Layer for Discord. This class is a thin wrapper around the
    discord.Client that handles receiving events and delegating all logic
    to the service layer. It contains delivery-specific logic but no business logic.
    """

    def __init__(
        self,
        token: str,
        organization_id: int,
        message_service: MessageService,
        **options,
    ):
        """
        Initializes the bot with its configuration and a MessageService instance.
        """
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents, **options)

        self.token = token
        self.organization_id = organization_id
        self.message_service = message_service
        self.message_limit = int(os.getenv('DISCORD_MESSAGE_LIMIT', 2000))

    async def send_in_chunks(self, channel, text: str):
        """
        Sends a long string of text in chunks, respecting the Discord message limit
        and preserving line integrity. This is DELIVERY logic.
        """
        if not text:
            return

        ai_chunks = text.split('[SPLIT]')
        
        for ai_chunk in ai_chunks:
            if not ai_chunk.strip():
                continue
            
            remaining_text = ai_chunk.strip()
            while len(remaining_text) > 0:
                if len(remaining_text) <= self.message_limit:
                    await channel.send(remaining_text)
                    break

                split_at = remaining_text.rfind('\\n', 0, self.message_limit)
                
                if split_at == -1:
                    split_at = self.message_limit

                chunk_to_send = remaining_text[:split_at]
                remaining_text = remaining_text[split_at:].lstrip()
                
                if chunk_to_send:
                    await channel.send(chunk_to_send)

    async def on_ready(self):
        logger.info(f"Bot for org {self.organization_id} logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user or not self.user.mentioned_in(message):
            return

        content = message.content.replace(f'<@!{self.user.id}>', '').strip()
        attachment_urls = [att.url for att in message.attachments]

        response_text, err = await self.message_service.process_discord_message(
            organization_id=self.organization_id,
            channel_id=str(message.channel.id),
            author_id=str(message.author.id),
            content=content,
            attachment_urls=attachment_urls,
        )

        if response_text:
            await self.send_in_chunks(message.channel, response_text)
        
        if err:
            logger.error(f"An error occurred while processing the message: {err}")

    async def start_bot(self):
        """
        Starts the bot's connection to Discord and handles login failures.
        """
        try:
            await self.start(self.token)
        except discord.errors.LoginFailure:
            logger.error(
                f"Login failed for bot belonging to organization {self.organization_id}. "
                f"The token is likely incorrect or expired. The bot will not start."
            )
        except Exception as e:
            logger.error(
                f"An unexpected error occurred for bot in organization {self.organization_id}: {e}",
                exc_info=True
            )
