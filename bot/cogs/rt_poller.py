from __future__ import annotations
import os
import aiohttp
import discord
from discord.ext import commands, tasks

from services.fetch_gtfs_rt import RTClient
from services.cache_gtfs_rt import RTStore

# Share a single RTStore instance across cogs via bot.rt_store

class RTPoller(commands.Cog):
    def __init__(self, bot: commands.Bot, store: RTStore):
        self.bot = bot
        self.store = store

        # Headers for Octopus GTFS-RT API
        self.headers = {
            "Ocp-Apim-Subscription-Key": os.getenv("OCTRANSPO_API_KEY")
        }

        # Log channel ID
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if self.log_channel_id == 0:
            raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")

        # GTFS-RT feed URLs
        self.trip_updates_url = os.getenv("GTFS_RT_TRIP_UPDATES_URL")
        self.vehicle_positions_url = os.getenv("GTFS_RT_VEHICLE_POSITIONS_URL")
        if not self.trip_updates_url or not self.vehicle_positions_url:
            raise RuntimeError("Missing GTFS_RT_TRIP_UPDATES_URL / GTFS_RT_VEHICLE_POSITIONS_URL in .env")

        self.session = aiohttp.ClientSession()
        self.client = RTClient(self.session)

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

    @tasks.loop(seconds=45)
    async def poll(self):
        try:
            vp = await self.client.fetch_vehicle_positions(self.vehicle_positions_url, self.headers)
            await self.store.update_vehicle_positions(vp)
        except Exception as e:
            await self.log("Error polling GTFS-RT vehicle feeds: " + str(e))
            pass
        try:
            tu = await self.client.fetch_trip_updates(self.trip_updates_url, self.headers)
            await self.store.update_trip_updates(tu)
        except Exception as e:
            await self.log("Error polling GTFS-RT trip update feeds: " + str(e))
            pass

    @poll.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    # Create ONE shared store and attach it to the bot for other cogs to use.
    store = RTStore(max_age_s=90)
    bot.rt_store = store  # simple shared reference
    await bot.add_cog(RTPoller(bot, store))
