# Filter and sorts the RSS feed entries
# Filter via: Date, Category (type), Route, Stop, station, keywords in title/content
# Max cap on number of entries: 15
# Allow user to chose number of entries to return (up to max)@
# Returns filtered/sorted list of entries
# Fetches feed via shared store


from typing import List, Dict, Any
from datetime import datetime
from bot.services.cache_rss import RSSStore, RSSFeed
import sqlite3

# Fetch from static SQLite DB from stop_code, return stop_id & stop_name
def get_stop_info(stop_code: str) -> Dict[str, Any]:
    con = sqlite3.connect("gtfs_static.db")
    cur = con.cursor()
    cur.execute("SELECT stop_id, stop_name FROM stops WHERE stop_code = ?", (stop_code,))
    row = cur.fetchone()
    con.close()
    if row:
        return {"stop_id": row[0], "stop_name": row[1]}
    else:
        return {}