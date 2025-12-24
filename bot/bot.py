import sys
import os
## Stupid asf fix but didn't work without it...
# Ensure project root is on sys.path when running this file directly so package imports like 'bot.cogs' work.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import discord
from discord.ext import commands
import dotenv

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        for fn in os.listdir("./bot/cogs"):
            if fn.endswith(".py") and fn != "__init__.py":
                await self.load_extension(f"bot.cogs.{fn[:-3]}")
        synced = await self.tree.sync()
        print(f"Synced {len(synced)} command(s): {[c.name for c in synced]}")

    async def on_ready(self):
        print(f"Bot is online as {self.user}")

if __name__ == "__main__":
    bot = MyBot()
    bot.run(TOKEN)