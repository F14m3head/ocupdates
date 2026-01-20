from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import time
import asyncio

from .fetch_rss import RSSFeed

# Data class to hold snapshots of RSS feeds
@dataclass
class RSSSnapshot:
    feed: Optional[RSSFeed] = None

class RSSStore:
    def __init__(self, max_age_s: int = 300):
        self.max_age_s = max_age_s
        self._lock = asyncio.Lock()
        self._snap = RSSSnapshot()

    async def update_feed(self, feed: RSSFeed) -> None:
        async with self._lock:
            self._snap.feed = feed
    
    async def get_snapshot(self) -> RSSSnapshot:
        async with self._lock:
            return self._snap
        
    def is_fresh(self, feed: Optional[RSSFeed]) -> bool:
        if not feed:
            return False
        now = time.time()
        return (now - feed.fetched_at) <= self.max_age_s