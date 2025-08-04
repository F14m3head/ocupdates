import discord
import io
from discord import app_commands
from discord.ext import commands
from bot.routes.alerts import get_alerts
import json

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update", description="Check for status updates directly from OC Transpo")
    async def update(self, interaction: discord.Interaction):
        try:
            # call the API to get the latest updates
            alerts = get_alerts()
            output = json.dumps(alerts, indent=2, ensure_ascii=False)

            # Check for errors
            if len(output) <= 1900:
                await interaction.response.send_message(f"Success:\n```\n{output}\n```")
            else:
                file = discord.File(io.StringIO(output), filename="update.txt")
                await interaction.response.send_message("Success (output too long, see attached file):", file=file)
                
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")             
                    
async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCog(bot))