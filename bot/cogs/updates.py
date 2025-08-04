import discord
import io
import subprocess
from discord import app_commands
from discord.ext import commands

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="update", description="Check for status updates directly from OC Transpo")
    async def update(self, interaction: discord.Interaction, number: app_commands.Range[int, 1, None]):
        try:
            # Call parser and pass number
            result = subprocess.run(
                ['python', 'bot/parser.py', str(number)],
                capture_output=True,
                text=True
            )

            # Check for errors
            if result.returncode == 0:
                output = result.stdout
                if len(output) <= 1900:
                    await interaction.response.send_message(f"Success:\n```\n{output}\n```")
                else:
                    file = discord.File(io.StringIO(output), filename="update.txt")
                    await interaction.response.send_message(file=file)
            else:
                error = result.stderr
                if len(error) <= 1900:
                    await interaction.response.send_message(f"Failed:\n```\n{error}\n```")
                else:
                    file = discord.File(io.StringIO(error), filename="error.txt")
                    await interaction.response.send_message(file=file)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")             
                    
async def setup(bot: commands.Bot):
    await bot.add_cog(UpdateCog(bot))