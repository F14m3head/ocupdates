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
    since: Optional[datetime.datetime] = None,
    limit: Optional[int] = None,
) -> list[dict]:
    results = []

    for e in entries:
        # Category
        if category and category.lower() not in {c.lower() for c in e.get("categories", [])}:
            continue

        # Route
        if route and route not in e.get("routes", set()):
            continue

        # Stop (supports ID or name)
        if stop:
            stop_l = stop.lower()
            if not any(stop_l in s.lower() for s in e.get("stops", set())):
                continue

        # Date
        if since:
            published = e.get("published")
            if not published or published < since:
                continue

        results.append(e)

    # Sort newest first
    results.sort(
        key=lambda e: e.get("published") or datetime.datetime.min,
        reverse=True,
    )

    return results[:limit] if limit is not None else results

# Fetches stop_id and stop_name from stop_code from GTFS static db
def fetch_GTFS_stops(db_path: str, stop_code: str):
    import sqlite3

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute("SELECT stop_id, stop_name FROM stops WHERE stop_code = ?", (stop_code,))
    rows = cur.fetchall()

    stop_dict = {row[0]: row[1] for row in rows}

    con.close()
    return stop_dict
