from __future__ import annotations
import os
import discord
from discord.ext import commands, tasks

from bot.services.fetch_rss import RSSClient
from bot.services.cache_rss import RSSStore

# Share a single RSSStore instance across cogs via bot.rss_store
class RSSPoller(commands.Cog):
    def __init__(self, bot: commands.Bot, store: RSSStore):
        self.bot = bot
        self.store = store

        self.rss_feed_url = os.getenv("RSS_FEED_URL", "")
        if not self.rss_feed_url:
            self.log("RSS_FEED_URL is not set in .env")
            raise RuntimeError("RSS_FEED_URL is missing in .env")

        # Log channel ID
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if self.log_channel_id == 0:
            raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")

        self.client = RSSClient()

        self.poll.start()

    def cog_unload(self):
        self.poll.cancel()
        self.bot.loop.create_task(self.session.close())

    # -- Helper to get the log channel --    
    async def get_log_channel(self) -> discord.TextChannel | None:
        ch = self.bot.get_channel(self.log_channel_id)
        if ch is None:
            try:
                ch = await self.bot.fetch_channel(self.log_channel_id)
            except Exception:
                return None
        return ch if isinstance(ch, discord.TextChannel) else None
    
    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        ch = await self.get_log_channel()
        if ch:
            try:
                await ch.send(msg)
            except Exception:
                pass

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
    bot.rss_store = store  # simple shared reference
    await bot.add_cog(RSSPoller(bot, store))