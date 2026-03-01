import logging
import discord
from service.message_service import MessageService

logger = logging.getLogger(__name__)


class StatelessDiscordBot(discord.Client):
    """
    The Delivery Layer for Discord. This class is a thin wrapper around the
    discord.Client that handles receiving events and delegating all logic
    to the service layer. It contains no business logic.
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
        :param token: The Discord bot token.
        :param organization_id: The organization this bot instance belongs to.
        :param message_service: The service responsible for processing messages.
        """
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents, **options)

        self.token = token
        self.organization_id = organization_id
        self.message_service = message_service

    async def on_ready(self):
        """
        Event handler for when the bot successfully logs in.
        """
        logger.info(f"Bot for org {self.organization_id} logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        """
        Event handler for when a message is received.
        :param message: The Discord message object.
        """
        # 1. Guard clauses: Ignore messages from the bot itself or if not mentioned.
        if message.author == self.user or not self.user.mentioned_in(message):
            return

        # 2. Extract raw data from the Discord message object.
        content = message.content.replace(f'<@!{self.user.id}>', '').strip()
        attachment_urls = [att.url for att in message.attachments]

        # 3. Delegate all logic to the service layer.
        response_text, err = await self.message_service.process_discord_message(
            organization_id=self.organization_id,
            channel_id=str(message.channel.id),
            author_id=str(message.author.id),
            content=content,
            attachment_urls=attachment_urls,
        )

        # 4. Send the response from the service back to the channel.
        if response_text:
            await message.channel.send(response_text)
        
        # The service layer is responsible for logging the error, so we don't need to here.

    async def start_bot(self):
        """
        Starts the bot's connection to Discord.
        """
        await self.start(self.token)
