# Filter and sorts the RSS feed entries
# Filter via: Date, Category (type), Route, Stop, station, keywords in title/content
# Allow user to chose number of entries to return (up to max)@
# Returns filtered/sorted list of entries

from __future__ import annotations
import datetime
import os
from typing import Iterable, Optional

# Get root/data dir
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(root_dir, "data")

def filter_alerts(
    entries: Iterable[dict],
    *,
    category: Optional[str] = None,
    route: Optional[str] = None,
    stop: Optional[str] = None,
    since: Optional[int] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    results = []
    
    # Put imput since into readable datetime
    since_dt = None
    if since is not None:
        since_dt = datetime.datetime.now() - datetime.timedelta(hours=since)
    

    for e in entries:
        # Category
        if category and category.lower() not in {c.lower() for c in e.get("categories", [])}:
            continue

        # Route
        if route and route not in e.get("routes", set()):
            continue

        # Stop
        if stop:
            stop_l = stop.lower()
            if not any(stop_l in s.lower() for s in e.get("stops", set())):
                continue
        
        # Date filtering - Note: relies on 'published' field being properly formatted as datetime
        if since_dt:
            published_str = e.get("published")
            if not published_str:
                continue
            try:
                published_dt = datetime.datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %Z")
            except ValueError:
                raise ValueError(f"Invalid date format in entry: {published_str}")
            if published_dt < since_dt:
                continue

        results.append(e)

    # Sort newest first
    #results.sort(
    #    key=lambda e: e.get("published") or datetime.datetime.min,
    #    reverse=True,
    #)

    return results[:limit] if limit is not None else results
