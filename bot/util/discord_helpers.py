from __future__ import annotations
from discord.ext import commands
import discord
import os

log_channel_raw = os.getenv('LOG_CHANNEL_ID', "0")
try:
    log_channel_id = int(log_channel_raw)
except ValueError as exc:
    raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env") from exc
if log_channel_id == 0:
    raise RuntimeError("LOG_CHANNEL_ID is missing/invalid in .env")


async def get_log_channel(bot: commands.Bot) -> discord.TextChannel | None:
    # Return cached channel if available (cache is per-bot instance)
    cached_ch = getattr(bot, "_cached_log_channel", None)
    if cached_ch is not None:
        return cached_ch

    # Try bot cache first (no API call)
    ch = bot.get_channel(log_channel_id)
    if ch is not None and isinstance(ch, discord.TextChannel):
        setattr(bot, "_cached_log_channel", ch)
        return ch

    # Fetch from API if not cached (only happens once per bot)
    try:
        ch = await bot.fetch_channel(log_channel_id)
        if isinstance(ch, discord.TextChannel):
            setattr(bot, "_cached_log_channel", ch)
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