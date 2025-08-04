import feedparser
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

FEED_URL = "https://www.octranspo.com/en/feeds/updates-en/"
ALERT_FILE = "backend/data/alerts.json" 

def load_existing_alerts():
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_alerts(data):
    with open(ALERT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_feed():
    feed = feedparser.parse(FEED_URL)
    current_alerts = {}
    seen_guids = set()

    for entry in feed.entries:
        guid = entry.get("id") or entry.get("guid") or entry.link
        seen_guids.add(guid)

        categories = []
        affected_routes = []

        if "tags" in entry:
            for tag in entry.tags:
                value = tag.get("term", "").strip()
                if value.startswith("affectedRoutes-"):
                    route_string = value.replace("affectedRoutes-", "")
                    affected_routes = [r.strip() for r in route_string.split(",")]
                else:
                    categories.append(value)

        current_alerts[guid] = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": clean_html(entry.summary),
            "categories": categories,
            "affected_routes": affected_routes
        }

    # Load previous alerts
    existing_alerts = load_existing_alerts()

    # Remomves the old shit
    removed_guids = set(existing_alerts.keys()) - seen_guids
    new_guids = seen_guids - set(existing_alerts.keys())

    # ERROR HANDLING of some sort (Kinda useles in prod)
    if removed_guids:
        print(f"Removed {len(removed_guids)} old alert(s).")
    if new_guids:
        print(f"Added {len(new_guids)} new alert(s).")

    # Save updated current alerts
    save_alerts(current_alerts)
    
    # Same shit as abovee
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Feed sync complete. {len(current_alerts)} active alerts.")

def clean_html(html, allowed_tags={"strong", "br", "p"}): # Changee Depending on the use case (Could change if using sys for embed or filtering)
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()  

    return str(soup)

if __name__ == "__main__":
    sync_feed()