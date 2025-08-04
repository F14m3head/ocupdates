import discord
from discord import app_commands
from discord.ext import commands
#from bot.routes.alerts import get_alerts

class AlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(AlertsCog(bot))