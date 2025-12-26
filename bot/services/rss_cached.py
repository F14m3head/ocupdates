from typing import Any, Dict
from cache import TTLCache
from rss_parser import sync_feed
import asyncio

# Not 100% sure how it works tbh, I am leanring it as I go.
# Heavily commented to help in trouble shooting

# !! NOT TESTED NOR USED YET !!

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

if __name__ == "__main__":

    async def main():
        cache = TTLCache(default_ttl=30.0)
        rss_service = RSSService(cache=cache, ttl_seconds=10.0)

        feed_url = "https://www.octranspo.com/en/feeds/updates-en/"
        feed_data = await rss_service.get_feed(feed_url)
        print(feed_data)

    asyncio.run(main())