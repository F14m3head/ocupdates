from __future__ import annotations
import os
import discord
from discord.ext import commands, tasks

from bot.services.fetch_rss import RSSClient
from bot.services.cache_rss import RSSStore

from bot.util.discord_helpers import log_to_channel


# Share a single RSSStore instance across cogs via bot.rss_store
class RSSPoller(commands.Cog):
    def __init__(self, bot: commands.Bot, store: RSSStore):
        self.bot = bot
        self.store = store

        self.rss_feed_url = os.getenv("RSS_FEED_URL", "")
        if not self.rss_feed_url:
            raise RuntimeError("RSS_FEED_URL is missing in .env")

        self.client = RSSClient()

        self.poll.start()

    async def cog_unload(self):
        self.poll.cancel()

    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        await log_to_channel(self.bot, msg)

    @tasks.loop(minutes=5)
    async def poll(self):
        rss_store: RSSStore = self.store

        try:
            feed = await self.client.fetch_feed(self.rss_feed_url)
            await rss_store.update_feed(feed)
        except Exception as e:
            await self.log(f"Error fetching RSS feed from {self.rss_feed_url}: {e}")

    @poll.before_loop
    async def before_poll(self) -> None:
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    # Create a shared store and attach it to the bot for other cogs to use.
    store = RSSStore(max_age_s=300)
    setattr(bot, "rss_store", store)  # simple shared reference
    await bot.add_cog(RSSPoller(bot, store))