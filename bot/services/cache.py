import time
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, Optional

# Basic in-memory TTL cache implementation
# Not 100% sure how it works tbh, I am leanring it as I go.
# Heavily commented to help in trouble shooting

# !! NOT TESTED NOR USED YET !!

@dataclass
class CacheEntry:
    value: Any
    expires_at: float

class TTLCache:
    def __init__(self, default_ttl: float = 30.0):
        self.default_ttl = float(default_ttl)
        self._data: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        now = time.time()
        async with self._lock:
            entry = self._data.get(key)
            if not entry:
                return None
            if entry.expires_at <= now:
                self._data.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        ttl = self.default_ttl if ttl is None else float(ttl)
        expires_at = time.time() + ttl
        async with self._lock:
            self._data[key] = CacheEntry(value=value, expires_at=expires_at)
