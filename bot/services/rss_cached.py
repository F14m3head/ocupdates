from typing import Any, Dict
from .cache import TTLCache
from .rss_parser import sync_feed

# Not 100% sure how it works tbh, I am leanring it as I go.
# Heavily commented to help in trouble shooting

class RSSService:
    def __init__(self, cache: TTLCache, ttl_seconds: float = 20.0):
        self.cache = cache
        self.ttl_seconds = ttl_seconds

    async def get_feed(self, url: str) -> Dict[str, Any]:
        key = f"rss:{url}"

        cached = await self.cache.get(key)
        if cached is not None:
            return cached

        # feedparser is synchronous; this will block briefly.
        # For light usage it's fine. For heavier usage, move to asyncio.to_thread.
        data = sync_feed(url)

        await self.cache.set(key, data, ttl=self.ttl_seconds)
        return data
