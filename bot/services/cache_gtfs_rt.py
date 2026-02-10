# Not 100% sure how it works tbh, I am leanring it as I go.
# Heavily commented to help in trouble shooting

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import time
import asyncio

from .fetch_gtfs_rt import RTFeed

# Data class to hold snapshots of real-time feeds
@dataclass
class RTSnapshot:
    trip_updates: Optional[RTFeed] = None
    vehicle_positions: Optional[RTFeed] = None

# Class to store and manage real-time GTFS feeds with freshness checks
class RTStore:
    def __init__(self, max_age_s: int = 90):
        self.max_age_s = max_age_s
        self._lock = asyncio.Lock()
        self._snap = RTSnapshot()

    # Update trip updates feed in a thread-safe manner
    async def update_trip_updates(self, feed: RTFeed) -> None:
        async with self._lock:
            self._snap.trip_updates = feed

    # Update vehicle positions feed in a thread-safe manner
    async def update_vehicle_positions(self, feed: RTFeed) -> None:
        async with self._lock:
            self._snap.vehicle_positions = feed

    # Retrieve the current snapshot in a thread-safe manner
    async def get_snapshot(self) -> RTSnapshot:
        async with self._lock:
            return self._snap

    # Check if a given feed is fresh based on its timestamp
    def is_fresh(self, feed: Optional[RTFeed]) -> bool:
        if not feed:
            return False
        # Prefer header timestamp if present; fallback to fetched_at
        now = time.time()
        if feed.header_ts:
            return (now - feed.header_ts) <= self.max_age_s
        return (now - feed.fetched_at) <= self.max_age_s
