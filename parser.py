# parser.py
import feedparser
import json

RSS_URL = "https://www.octranspo.com/feeds/updates-en/"

def parse_feed():
    feed = feedparser.parse(RSS_URL)
    entries = []

    for entry in feed.entries[:5]:  # limit to latest 5 updates
        entries.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.summary
        })

    return entries

if __name__ == "__main__":
    updates = parse_feed()
    print(json.dumps(updates))
