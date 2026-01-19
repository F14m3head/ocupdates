# Create auto command send to private channel incase of errors at parsing level
# Either call to test on each parse request or by use call. > verify RSS feed is getting correct status and data
# If fails, auto send to admin channel the error for review 
# AND send "Error on our end, please try again later" to user.


# Adds 2 commands, 
# 1: Shows status of RSS feed (Time fetch, size(# of lines), if it is expeired)
# 2: Shows status of RT feed (Time fetch, size$(# of entrys), if it is expeired)


from discord.ext import commands
from discord import app_commands
import discord
import os
import time


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        
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
    
    @app_commands.command(name="rss_status", description="Check the status of the RSS feed")
    async def rss_status(self, interaction: discord.Interaction):
        # Enforce guild restriction
        if self.allowed_guild_id is not None and interaction.guild_id != self.allowed_guild_id:
            try:
                await interaction.response.send_message("This command cannot be used in this server.", ephemeral=True)
            except Exception:
                pass
            return
        await interaction.response.send_message("RSS feed status checked. (Placeholder response)")
        # Placeholder for actual RSS status logic

    
    @app_commands.command(name="rt_status", description="Check the status of the RT feed")
    async def rt_status(self, interaction: discord.Interaction):
        # Enforce guild restriction
        if self.allowed_guild_id is not None and interaction.guild_id != self.allowed_guild_id:
            try:
                await interaction.response.send_message("This command cannot be used in this server.", ephemeral=True)
            except Exception:
                pass
            return
        
        # Pull the shared RT store from the bot
        store = getattr(self.bot, "rt_store", None)
        if store is None:
            try:
                await interaction.response.send_message("RT store is not available.", ephemeral=True)
            except Exception as e:
                await self.log(f"Error fetching RT shared store: {e}")
            return

        try:
            snap = await store.get_snapshot()
        except Exception as e:
            await interaction.response.send_message(f"Error fetching RT snapshot: {e}", ephemeral=True)
            await self.log(f"Error fetching RT snapshot: {e}")
            return

        def _count_entities(feed) -> str:
            if not feed:
                return "0"
            # Try common attributes that may hold entities
            for attr in ("entities", "entity", "trip_updates", "vehicle_positions", "entity_list"):
                val = getattr(feed, attr, None)
                if val is not None:
                    try:
                        return str(len(val))
                    except Exception:
                        break
            # Fallback: unknown
            return "?"

        def _fmt_time(ts) -> str:
            try:
                return time.ctime(ts)
            except Exception:
                return str(ts)

        tu = snap.trip_updates
        vp = snap.vehicle_positions

        tu_count = _count_entities(tu)
        vp_count = _count_entities(vp)

        tu_header = getattr(tu, "header_ts", None) if tu else None
        tu_fetched = getattr(tu, "fetched_at", None) if tu else None
        vp_header = getattr(vp, "header_ts", None) if vp else None
        vp_fetched = getattr(vp, "fetched_at", None) if vp else None

        tu_fresh = store.is_fresh(tu)
        vp_fresh = store.is_fresh(vp)

        msg_lines = [
            "RT feed status:",
            f"- TripUpdates: entries={tu_count}; header_ts={_fmt_time(tu_header) if tu_header else 'N/A'}; fetched_at={_fmt_time(tu_fetched) if tu_fetched else 'N/A'}; {'fresh' if tu_fresh else 'stale'}",
            f"- VehiclePositions: entries={vp_count}; header_ts={_fmt_time(vp_header) if vp_header else 'N/A'}; fetched_at={_fmt_time(vp_fetched) if vp_fetched else 'N/A'}; {'fresh' if vp_fresh else 'stale'}",
        ]

        try:
            await interaction.response.send_message("\n".join(msg_lines))
        except Exception:
            # If responding fails, at least log the message
            await self.log("Failed to send rt_status response: " + " | ".join(msg_lines))
        
        
async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
    