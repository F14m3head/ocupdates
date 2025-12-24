import feedparser
import re
from bs4 import BeautifulSoup
from typing import Any, Dict, List

feed_url = "https://www.octranspo.com/en/feeds/updates-en/"

# !! NOT USED YET !!

# -- HTML CLEANING FUNCTION -- 
# Might be outdated/unoptimal, but works for now. (Copied form old parser)
def clean_html(html_content):

    # Try using lxml for speed, fall back if not installed
    try:
        soup = BeautifulSoup(html_content, 'lxml')
    except Exception:
        soup = BeautifulSoup(html_content, 'html.parser')

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
                    if "Stop" in head: head = f"🛑 {head}"
                    elif "Route" in head: head = f"🚌 {head}"
                    elif "Alternate" in head: head = f"🔄 {head}"
                    
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

# Outdate, use for testing if needed to print ouput
def fetch_feed(feed_url):
    
    try: 
        feed = feedparser.parse(feed_url)

    except Exception as e:
        print(f"Error fetching feed: {e}")
        return

    # Check the status code to ensure a successful fetch
    if feed.status == 200:
        print(f"Successfully fetched feed: {feed.feed.title}")
        print(f"Website Link: {feed.feed.link}")
        print(f"Description: {feed.feed.description}")
    else:
        print(f"Failed to fetch RSS feed. Status code: {feed.status}")

    # Iterate over the entries and print details
    print("\n--- Entries ---")
    for entry in feed.entries:
        print(f"Title: {entry.title}")
        print(f"Link: {entry.link}")
        # Checks incase some fields are missing from the feed.entry
        if 'published' in entry:
            print(f"Published Date: {entry.published}")
        if 'description' in entry:
            clean_descripition = clean_html(entry.description)
            print(f"description: {clean_descripition}")
        if 'category' in entry:
            print(f"categories: {entry.category}")
        else:
            print("categories: N/A")
        print("-" * 20)
    return feed

# -- RSS PARSING FUNCTION --
def parse_feed(feed_url: str) -> Dict[str, Any]:
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        return {
            "ok": "Error at pulling feed",
            "status": None,
            "error": str(e),
            "url": feed_url,
        }

    if getattr(feed, "status", None) != 200:
        return {
            "ok": getattr(feed, "status", False) ,
            "status": getattr(feed, "status", None),
            "error": "Failed to fetch feed",
            "url": feed_url,
        }

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
            "published": getattr(entry, "published", None),
            "description": clean_html(getattr(entry, "description", None)),
            "category": getattr(entry, "category", None),
        })

    return {
        "ok": True,
        "status": 200,
        "meta": meta,
        "entries": entries,
        "url": feed_url,
    }

def sync_feed():
    return parse_feed(feed_url)

#-- TESTING THE PARSER FUNCTIONALITY --
#print("Fetching and parsing feed...")
#print(parse_feed(feed_url))
