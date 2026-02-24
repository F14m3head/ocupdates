# Create auto command send to private channel incase of errors at parsing level
# Either call to test on each parse request or by use call. > verify RSS feed is getting correct status and data
# If fails, auto send to admin channel the error for review 
# AND send "Error on our end, please try again later" to user.

# Adds 4 commands, 
# 1: Shows status of RSS feed (Time fetch, size(# of lines), if it is expeired)
# 2: Shows status of RT feed (Time fetch, size$(# of entrys), if it is expeired)
# 3: Reload a cog by name
# 4: List loaded cogs


from discord.ext import commands
from discord import app_commands
import discord
import os
import time

from bot.util.discord_helpers import log_to_channel

DEV_GUILD = int(os.getenv("DEV_GUILD_ID", "0")) if os.getenv("DEV_GUILD_ID") else 0
print(f"AdminCog DEV_GUILD set to: {DEV_GUILD if DEV_GUILD else 'None'}")

class AdminCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot  

        # Allowed guild ID for command restriction
        allowed = os.getenv("ALLOWED_GUILD_ID", "").strip()
        try:
            self.allowed_guild_id = int(allowed) if allowed else None
        except ValueError:
            self.allowed_guild_id = None
    
    # -- Helper to log messages to the log channel --
    async def log(self, msg: str) -> None:
        await log_to_channel(self.bot, msg)

    # -- Helpers --
    def loaded_extensions(self) -> list[str]:
        # These are full extension paths: bot.cogs.example
        return sorted(self.bot.extensions.keys()) 
   
    # -- Autocomplete for cog names --
    async def cog_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=ext, value=ext)
            for ext in self.loaded_extensions()
            if current.lower() in ext.lower()
        ][:25]

    @app_commands.command(name="rss_status", description="Check the status of the RSS feed")
    @app_commands.guilds(DEV_GUILD)
    async def rss_status(self, interaction: discord.Interaction):
        await interaction.response.defer()
                # Enforce guild restriction
        if self.allowed_guild_id is not None and interaction.guild_id != self.allowed_guild_id:
            try:
                await interaction.followup.send("This command cannot be used in this server.", ephemeral=True)
            except Exception:
                await self.log("Failed to notify user about guild restriction")
            return
        
        # Pull the shard RSS store from the bot
        store = getattr(self.bot, "rss_store", None)
        if store is None:
            try:
                await interaction.followup.send("RSS store is not available.", ephemeral=True)
            except Exception as e:
                await self.log(f"Error sending RSS store not available message: {e}")
            return
        
        # Fetch snapshot
        try:
            snap = await store.get_snapshot()
        except Exception as e:
            try:
                await interaction.followup.send(f"Error fetching RSS snapshot: {e}", ephemeral=True)
            except Exception:
                await self.log(f"Error fetching RSS snapshot (notify failed): {e}")
            await self.log(f"Error fetching RSS snapshot: {e}")
            return
        
        # Analyze feed
        service_status_feed = snap.feed
        
        def _count_entities(feed) -> str:
            if not feed:
                return "0"
            # Try common attributes that may hold entities
            for attr in ("entries",):
                val = getattr(feed, attr, None)
                if val is not None:
                    try:
                        return str(len(val))
                    except Exception:
                        break
            # Fallback: unknown
            return "?"
        
        # Analyze snapshot
        entry_count = _count_entities(service_status_feed)
        last_fetched = getattr(service_status_feed, 'fetched_at', None) 
        meta = getattr(service_status_feed, 'meta', {})
        status = getattr(service_status_feed, 'status', None)
        ok = getattr(service_status_feed, 'ok', False)
        is_fresh = store.is_fresh(service_status_feed) if snap else False 
        
        # Build status message
        msg_lines = [   
            "RSS feed status:",
            f"- OK: {ok}",
            f"- HTTP Status: {status}",
            f"- Title: {meta.get('title', 'N/A')}",
            f"- Link: {meta.get('link', 'N/A')}",
            f"- Entries: {entry_count}",
            f"- Last fetched at: {time.ctime(last_fetched) if last_fetched else 'N/A'}", # Should return N/A
            f"- Status: {'fresh' if is_fresh else 'stale'}",
        ]
        
        # Send response
        try:
            await interaction.followup.send("\n".join(msg_lines))
        except Exception as e:
            await self.log("Failed to send rss_status response: " + " | ".join(msg_lines) + " | Error: " + str(e))
    
    @app_commands.command(name="rt_status", description="Check the status of the RT feed")
    @app_commands.guilds(DEV_GUILD)
    async def rt_status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        # Enforce guild restriction
        if self.allowed_guild_id is not None and interaction.guild_id != self.allowed_guild_id:
            try:
                await interaction.followup.send("This command cannot be used in this server.", ephemeral=True)
            except Exception:
                await self.log("Failed to notify user about guild restriction")
            return
        
        # Pull the shared RT store from the bot
        store = getattr(self.bot, "rt_store", None)
        if store is None:
            try:
                await interaction.followup.send("RT store is not available.", ephemeral=True)
            except Exception as e:
                await self.log(f"Error sending RT store not available message: {e}")
            return

        try:
            snap = await store.get_snapshot()
        except Exception as e:
            try:
                await interaction.followup.send(f"Error fetching RT snapshot: {e}", ephemeral=True)
            except Exception:
                await self.log(f"Error fetching RT snapshot (notify failed): {e}")
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
            await interaction.followup.send("\n".join(msg_lines))
        except Exception as e:
            # If responding fails, at least log the message
            await self.log("Failed to send rt_status response: " + " | ".join(msg_lines) + " | Error: " + str(e))
        
    @app_commands.command(name="reload", description="Reload a loaded cog")
    @app_commands.autocomplete(cog=cog_autocomplete)
    @app_commands.guilds(DEV_GUILD)
    async def reload(
        self,
        interaction: discord.Interaction,
        cog: str,
    ):
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message(
                "Permission denied.", ephemeral=True
            )

        try:
            await self.bot.reload_extension(cog)
            await interaction.response.send_message(
                f"Reloaded `{cog}`",
            )
            print(f"Reloaded cog: {cog}")
        except Exception as e:
            await interaction.response.send_message(
                f"Failed to reload `{cog}`\n```{e}```",
            )
            print(f"Failed to reload cog {cog}: {e}")

    @app_commands.command(name="cogs", description="List loaded cogs")
    @app_commands.guilds(DEV_GUILD)
    async def cogs(self, interaction: discord.Interaction):
        
        if not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message(
                "Permission denied.", ephemeral=True
            )

        exts = self.loaded_extensions()
        if not exts:
            return await interaction.response.send_message(
                "No cogs loaded."
            )

        await interaction.response.send_message(
            "**Loaded cogs:**\n" + "\n".join(f"• `{e}`" for e in exts),
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCog(bot))
    