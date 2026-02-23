from __future__ import annotations
from discord.ext import commands
import discord
import os

log_channel_id = int(os.getenv('LOG_CHANNEL_ID', "0"))
if log_channel_id == 0:
    raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")

# Cache the channel after first fetch
_cached_log_channel: discord.TextChannel | None = None

async def get_log_channel(bot: commands.Bot) -> discord.TextChannel | None:
    global _cached_log_channel
    
    # Return cached channel if available
    if _cached_log_channel is not None:
        return _cached_log_channel
    
    # Try bot cache first (no API call)
    ch = bot.get_channel(log_channel_id)
    if ch is not None and isinstance(ch, discord.TextChannel):
        _cached_log_channel = ch
        return ch
    
    # Fetch from API if not cached (only happens once)
    try:
        ch = await bot.fetch_channel(log_channel_id)
        if isinstance(ch, discord.TextChannel):
            _cached_log_channel = ch
            return ch
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        pass
    
    return None

async def log_to_channel(bot: commands.Bot, msg: str) -> None:
    ch = await get_log_channel(bot)
    if ch:
        try:
            await ch.send(msg)
        except (discord.Forbidden, discord.HTTPException):
            pass