# User facing commands
from discord.ext import commands
from discord import app_commands
import discord
import os


class QuerieCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Log channel ID
        self.log_channel_id = int(os.getenv("LOG_CHANNEL_ID", "0"))
        if self.log_channel_id == 0:
            raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")


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

    @app_commands.command(name="update", description="Check for status updates directly from OC Transpo")
    async def update(self, interaction: discord.Interaction, number: int = 5):
        await interaction.response.defer()

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
        
        def fetch_updates() -> list[str]:
            updates = []
            count = 0
            # Sends each alert in a separate message to limit character count
            for entry in snap.feed.entries:
                if count >= number:
                    break
                title = entry.get("title", "No Title")
                link = entry.get("link", "No Link")
                description = entry.get("description", "No Description")
                published = entry.get("published", "No Published Date")
                updates.append(f"**{title}**\nPublished: {published}\nDescription: {description}\nLink: {link}\n")
                count += 1
            return updates
        
        updates = fetch_updates()
        if not updates:
            await interaction.followup.send("No updates found.", ephemeral=True)
            return
        
        for update in updates:
            await interaction.followup.send(update)
                    
async def setup(bot: commands.Bot):
    await bot.add_cog(QuerieCog(bot))