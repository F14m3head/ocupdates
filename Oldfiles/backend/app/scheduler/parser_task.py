import asyncio
from backend.app.parser import sync_feed

async def run_parser_loop():
    while True:
        print("[Scheduler] Syncing feed…")
        await asyncio.to_thread(sync_feed)
        await asyncio.sleep(60)