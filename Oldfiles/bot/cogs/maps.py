import discord
from discord import app_commands
import os
from discord.ext import commands

class MapCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="map", description="Check a route map")
    async def map(self, interaction: discord.Interaction, route: str):
        if route == "e1":
            route = "e1 express"
        elif len(route) < 3 and len(route) > 0:
            if len(route) == 1:
                route = f"00{route}"
            else:
                route = f"0{route}"
        try:
            file_path = f"./bot/maps/png/{route}.png" # CHANGE FOR PROD
            if not os.path.exists(file_path):
                await interaction.response.send_message(f"No map found for route {route}", ephemeral=True)
                return

            file = discord.File(file_path, filename=f"{route}.png")
            await interaction.response.send_message(file=file)
        except Exception as e:
            await interaction.response.send_message(f"Error: {str(e)}")    

async def setup(bot: commands.Bot):
    await bot.add_cog(MapCog(bot))