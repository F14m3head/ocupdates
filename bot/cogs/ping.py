# This is just a test cog...
# Just a basic ping dummy command
## Used this shit to get the cog system working, for some reason it was buggin at the start


from discord.ext import commands
from discord import app_commands
import discord

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Replies with Pong!")
    async def ping(self, interaction: discord.Interaction):
        def get_latency():
            return round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! Took {get_latency()}ms")

async def setup(bot):
    await bot.add_cog(PingCog(bot))