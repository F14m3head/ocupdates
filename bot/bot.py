import discord
from discord import app_commands
from discord.ext import commands
import subprocess
import os
import dotenv
import io
from bot.routes.alerts import get_alerts

alerts = get_alerts()

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
        for cmd in synced:
            print(f"- {cmd.name}: {cmd.description}")
    except Exception as e:
        print(f"Failed to sync: {e}")
        
@bot.tree.command(name="update", description="Check for status updates directly from OC Transpo")
async def update(interaction: discord.Interaction, number: app_commands.Range[int, 1, None]):
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

@bot.tree.command(name="map", description="Check a route map")
async def map(interaction: discord.Interaction, route: str):
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

# Old syntax using !update
'''@bot.command()
async def update(ctx, number: int):
    try:
        # Call the parser.py script and pass the number
        result = subprocess.run(
            ['python', 'bot/parser.py', str(number)],
            capture_output=True,
            text=True
        )

        # Check for errors
        if result.returncode == 0:
            output = result.stdout
            if len(output) <= 1900:
                await ctx.send(f"Success:\n```\n{output}\n```")
            else:
                file = discord.File(io.StringIO(output), filename="update.txt")
                await ctx.send(file=file)
        else:
            error = result.stderr
            if len(error) <= 1900:
                await ctx.send(f"Failed:\n```\n{error}\n```")
            else:
                file = discord.File(io.StringIO(error), filename="error.txt")
                await ctx.send(file=file)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")'''

bot.run(TOKEN)
