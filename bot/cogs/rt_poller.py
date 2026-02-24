from __future__ import annotations
import os
import aiohttp
import discord
from discord.ext import commands, tasks

from services.fetch_gtfs_rt import RTClient
from services.cache_gtfs_rt import RTStore

from bot.util.discord_helpers import log_to_channel

# Share a single RTStore instance across cogs via bot.rt_store

class RTPoller(commands.Cog):
    def __init__(self, bot: commands.Bot, store: RTStore):
        self.bot = bot
        self.store = store

        # Headers for Octopus GTFS-RT API
        self.headers = {
            "Ocp-Apim-Subscription-Key": os.getenv("OCTRANSPO_API_KEY", "")
        }
        if not self.headers["Ocp-Apim-Subscription-Key"]:
            raise RuntimeError("OCTRANSPO_API_KEY is missing in .env")

        # GTFS-RT feed URLs
        self.trip_updates_url = os.getenv("GTFS_RT_TRIP_UPDATES_URL", "")
        self.vehicle_positions_url = os.getenv("GTFS_RT_VEHICLE_POSITIONS_URL", "")
        if not self.trip_updates_url or not self.vehicle_positions_url:
            raise RuntimeError(
                "Missing required environment variables: GTFS_RT_TRIP_UPDATES_URL and/or GTFS_RT_VEHICLE_POSITIONS_URL"
            )

        self.session = aiohttp.ClientSession()
        self.client = RTClient(self.session)

        self.poll.start()

    async def cog_unload(self):
        self.poll.cancel()
        self.bot.loop.create_task(self.session.close())

    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        await log_to_channel(self.bot, msg)

    @tasks.loop(seconds=45)
    async def poll(self):
        vp = None
        try:
            vp = await self.client.fetch_vehicle_positions(self.vehicle_positions_url, self.headers)
            await self.store.update_vehicle_positions(vp)
        except Exception as e:
            error_detail = ""
            vp_error = getattr(vp, "error", None)
            if vp_error:
                error_detail = "\n" + vp_error
            else:
                error_detail = "\nNo vehicle position feed result"
            await self.log(f"Error polling GTFS-RT vehicle position feeds: {str(e)}{error_detail}")
       
       
        tu = None
        try:
            tu = await self.client.fetch_trip_updates(self.trip_updates_url, self.headers)
            await self.store.update_trip_updates(tu)
        except Exception as e:
            error_detail = ""
            tu_error = getattr(tu, "error", None)
            if tu_error:
                error_detail = "\n" + tu_error
            else:
                error_detail = "\nNo trip update feed result"
            await self.log(f"Error polling GTFS-RT trip update feeds: {str(e)}{error_detail}")


    @poll.before_loop
    async def before_poll(self):
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    # Create ONE shared store and attach it to the bot for other cogs to use.
    store = RTStore(max_age_s=90)
    setattr(bot, "rt_store", store)  # simple shared reference
    await bot.add_cog(RTPoller(bot, store))
