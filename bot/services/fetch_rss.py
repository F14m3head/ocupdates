# Version 2 of RSS fetching service

# title
# link
# published
# description
# categories
# routes
# stops

import feedparser
import re
from bs4 import BeautifulSoup
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass
import time

@dataclass
class RSSFeed:
    ok: bool
    status: Optional[int]
    meta: Dict[str, Any]
    entries: List[Dict[str, Any]]
    fetched_at: float

class RSSClient:
    def __init__(self):
        pass

    async def close(self):
        pass

    async def fetch_feed(self, feed_url: str) -> RSSFeed:
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            return RSSFeed(
                ok=False,
                status=None,
                meta={},
                entries=[],
                fetched_at=time.time(),
            )

        if getattr(feed, "status", None) != 200:
            return RSSFeed(
                ok=False,
                status=getattr(feed, "status", None),
                meta={},
                entries=[],
                fetched_at=time.time(),
            )

        meta = {
            "title": getattr(feed.feed, "title", ""),
            "link": getattr(feed.feed, "link", ""),
            "description": getattr(feed.feed, "description", ""),
        }

        entries: List[Dict[str, Any]] = []
        for entry in feed.entries:
            entries.append({
                "title": getattr(entry, "title", ""),
                "link": getattr(entry, "link", ""),
                "categories": parse_tags(entry)[0],
                "routes": parse_tags(entry)[1],
                "published": getattr(entry, "published", None),
                "description": clean_html(getattr(entry, "description", None)),
                "stops": parse_stops(clean_html(getattr(entry, "description", None))),
            })

        return RSSFeed(
            ok=True,
            status=200,
            meta=meta,
            entries=entries,
            fetched_at=time.time()
        )
    
    async def sync_feed(self, feed_url: str) -> RSSFeed:
        return await self.fetch_feed(feed_url)

# -- HTML CLEANING FUNCTION --
# Might be outdated/unoptimal, but works for now. (Copied form old parser)
def clean_html(raw_html: str | None) -> str | None:

    # Return None if no HTML provided
    if raw_html is None:
        return None

    # Try using lxml for speed, fall back if not installed
    try:
        soup = BeautifulSoup(raw_html, 'lxml')
    except Exception:
        soup = BeautifulSoup(raw_html, 'html.parser')

    # --- 1. HANDLE TABLES ---
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if not rows:
            continue
            
        # Extract headers
        headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
        
        formatted_list = []
        
        # Loop through data rows
        for tr in rows[1:]:
            # --- FIX IS HERE: Use separator=", " to prevent text smashing ---
            cells = [td.get_text(separator=", ", strip=True) for td in tr.find_all('td')]
            
            if len(cells) == len(headers):
                item_lines = []
                for head, cell in zip(headers, cells):
                    # Add formatting icons
                    if "Stop" in head:
                        head = f"🛑 {head}"
                    elif "Route" in head:
                        head = f"🚌 {head}"
                    elif "Alternate" in head:
                        head = f"🔄 {head}"
                    
                    item_lines.append(f"**{head}:** {cell}")
                
                formatted_list.append("\n".join(item_lines))
        
        # Replace table with formatted text
        replacement_text = "\n\n".join(formatted_list)
        table.replace_with(f"\n{replacement_text}\n")

    # --- 2. CLEAN UP ---
    # Handle links
    for a in soup.find_all('a'):
        href = a.get('href')
        text = a.get_text(strip=True)
        if href and text:
            a.replace_with(f"{text} ({href})")
    
    # Extract remaining text with newlines
    text = soup.get_text(separator="\n")
    
    # Fix massive gaps
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()

# -- TAG PARSING FUNCTION --
# For categories and routes
def parse_tags(entry):
    categories = set()
    routes = set()
        
    for tag in getattr(entry, "tags", []):
        term = getattr(tag, "term", "").strip()
        if not term:
            continue

        lower = term.lower()

        if lower.startswith("affectedroutes-"):
            routes.add(term.split("-", 1)[1])

        else:
            categories.add(term)

    return categories, routes


# -- STOP PARSING FUNCTION --

# Matches: "3012"
STOP_ID_RE = re.compile(r"(#\d{4}|\(\d{4}\)|\d{4}\.)")
def parse_stops(cleaned_text: str | None) -> Set[str]:
    if not cleaned_text:
        return set()

    stops: Set[str] = set()

    for match in STOP_ID_RE.finditer(cleaned_text):
        stop_id = match.group(1)
        stop_id = re.sub(r"\D", "", stop_id)  # Remove non-digit characters
        if stop_id:
            stops.add(stop_id)
    return stops

# -- TIME FUNCTION --
# Returns reliable current from time.struct_time
## MAYBE? Not implemented yet
def current_time_seconds() -> float:
    return time.time()