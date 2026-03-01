import logging
import aiohttp
import discord

logger = logging.getLogger(__name__)

class StatelessDiscordBot:
    """
    A stateless Discord client that forwards all logic to a central API.
    """
    def __init__(self, token: str, organization_id: int, api_endpoint: str):
        self.token = token
        self.organization_id = organization_id
        self.api_endpoint = api_endpoint
        self.client = discord.Client(intents=self._get_intents())
        self._setup_events()

    def _get_intents(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        return intents

    def _setup_events(self):
        @self.client.event
        async def on_ready():
            logger.info(f"Bot for org {self.organization_id} logged in as {self.client.user}")

        @self.client.event
        async def on_message(message: discord.Message):
            if message.author == self.client.user or not self.client.user.mentioned_in(message):
                return

            payload = {
                "platform": "discord",
                "organization_id": self.organization_id,
                "channel_id": str(message.channel.id),
                "user_id": str(message.author.id),
                "content": message.content.replace(f'<@!{self.client.user.id}>', '').strip(),
                "attachment_urls": [att.url for att in message.attachments]
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_endpoint, json=payload) as response:
                        response.raise_for_status()
                        api_res = await response.json()
                        await message.channel.send(api_res.get("response", "Error: No response from API."))
            except aiohttp.ClientError as e:
                logger.error(f"API call failed for org {self.organization_id}: {e}")
                await message.channel.send("Sorry, I couldn't connect to the WatchTower engine.")

    async def start(self):
        """Starts the bot's connection to Discord."""
        await self.client.start(self.token)
