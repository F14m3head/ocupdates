import os
import asyncio
import datetime as dt
from zoneinfo import ZoneInfo

import dotenv
import discord
from discord.ext import commands, tasks
from discord import app_commands


from services.fetch_gtfs_static import fetch_gtfs
from services.gtfs_static_db import build_db_from_gtfs_zip

# Timezone for scheduling the daily GTFS update
# Note: Use "America/Toronto" for Eastern Time with DST handling
TORONTO_TZ = ZoneInfo("America/Toronto")

class Maintenance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._lock = asyncio.Lock()

        # Load configuration from .env
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dotenv.load_dotenv(os.path.join(root_dir, ".env"))

        # Log channel ID
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if self.log_channel_id == 0:
            raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")
        
        # Allowed guild ID for command restriction
        allowed = os.getenv("ALLOWED_GUILD_ID", "").strip()
        try:
            self.allowed_guild_id = int(allowed) if allowed else None
        except ValueError:
            self.allowed_guild_id = None

        # Data directory
        self.data_dir = os.path.join(root_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # GTFS ZIP and DB paths
        self.gtfs_zip_path = os.path.join(self.data_dir, "GTFSExport.zip")
        self.db_path = os.path.join(self.data_dir, "gtfs_static.sqlite")
        self.tmp_db_path = os.path.join(self.data_dir, "gtfs_static.tmp.sqlite")

        self.daily_gtfs_update.start()

    def cog_unload(self):
        self.daily_gtfs_update.cancel()

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

    # -- Daily GTFS update task --
    @tasks.loop(time=dt.time(hour=1, minute=30, tzinfo=TORONTO_TZ))
    async def daily_gtfs_update(self):
        await self.run_update(requested_by="schedule")
        async with self._lock:
            await self.log("**GTFS maintenance**: starting daily update (download + DB rebuild).")

            try:
                # Download GTFS ZIP
                await self.log("Downloading `GTFSExport.zip`…")
                zip_path, size_bytes = await asyncio.to_thread(fetch_gtfs, 60)
                await self.log(f"Download complete: `{size_bytes/1024/1024:.2f} MB` → `{os.path.basename(zip_path)}`")
                
                # Rebuild DB
                await self.log("Rebuilding SQLite DB…")
                def _progress_cb(msg: str):
                    try:
                        asyncio.run_coroutine_threadsafe(self.log(f"**GTFS DB**: {msg}"), self.bot.loop)
                    except Exception:
                        pass
                await asyncio.to_thread(build_db_from_gtfs_zip, self.gtfs_zip_path, self.tmp_db_path, _progress_cb)
                
                # Replace old DB with new
                os.replace(self.tmp_db_path, self.db_path)
                await self.log("DB rebuild complete. New `gtfs_static.sqlite` is live.")

            except Exception as e:
                await self.log(f"**GTFS maintenance failed**: `{type(e).__name__}: {e}`")
                # Cleanup temp DB if created
                try:
                    if os.path.exists(self.tmp_db_path):
                        os.remove(self.tmp_db_path)
                except Exception:
                    pass

    # -- Core update logic used by both daily task and manual command --
    async def run_update(self, requested_by: str | None = None) -> None:
        async with self._lock:
            prefix = "**GTFS maintenance**"
            if requested_by:
                prefix += f" (requested by {requested_by})"
            
            await self.log(f"{prefix}: starting update (download + DB rebuild).")
            
            try:
                # Download GTFS ZIP
                await self.log("Downloading `GTFSExport.zip`…")
                zip_path, size_bytes = await asyncio.to_thread(fetch_gtfs, 60)
                await self.log(f"Download complete: `{size_bytes/1024/1024:.2f} MB` → `{os.path.basename(zip_path)}`")
                # Rebuild DB
                await self.log("Rebuilding SQLite DB…")
                def _progress_cb(msg: str):
                    try:
                        asyncio.run_coroutine_threadsafe(self.log(f"**GTFS DB**: {msg}"), self.bot.loop)
                    except Exception:
                        pass
                await asyncio.to_thread(build_db_from_gtfs_zip, self.gtfs_zip_path, self.tmp_db_path, _progress_cb)
                # Replace old DB with new
                os.replace(self.tmp_db_path, self.db_path)
                await self.log("DB rebuild complete. New `gtfs_static.sqlite` is live.")

            except Exception as e:
                await self.log(f"**GTFS maintenance failed**: `{type(e).__name__}: {e}`")
                try:
                    if os.path.exists(self.tmp_db_path):
                        os.remove(self.tmp_db_path)
                except Exception:
                    pass
                raise
    
    # -- Manual command to trigger GTFS update --
    @app_commands.command(name="gtfs_update", description="Manually download GTFS static and rebuild the SQLite DB.")
    @app_commands.checks.has_permissions(administrator=True)
    async def gtfs_update(self, interaction: discord.Interaction):
        # Enforce guild restriction
        if self.allowed_guild_id is not None and interaction.guild_id != self.allowed_guild_id:
            try:
                await interaction.response.send_message("This command cannot be used in this server.", ephemeral=True)
            except Exception:
                pass
            return

        await interaction.response.defer(thinking=True)

        try:
            who = interaction.user.mention
            await self.run_update(requested_by=who)
            await interaction.followup.send("GTFS update finished successfully.")
        except Exception:
            await interaction.followup.send("GTFS update failed. Check the log channel for details.")

    # -- Daily GTFS update task --
    @daily_gtfs_update.before_loop
    async def before_daily_gtfs_update(self):
        await self.bot.wait_until_ready()
        await self.log("Maintenance loaded.\nDaily GTFS update scheduled for **01:30 America/Toronto**.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Maintenance(bot))