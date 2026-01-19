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
    async def update(self, interaction: discord.Interaction):
        await interaction.response.send_message("PLACE HOLLDER FOR STATUS UPDATE COMMAND")
        # Placeholder for actual update logic  
                    
async def setup(bot: commands.Bot):
    await bot.add_cog(QuerieCog(bot))