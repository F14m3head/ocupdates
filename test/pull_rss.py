# Used for testing
# Pulls RSS feed from OCtranspo
# Downloads the file as a .txt

import feedparser
import pprint
feed_url = "https://www.octranspo.com/en/feeds/updates-en/"

feed = feedparser.parse(feed_url)

with open("test/oc_rss_feed.txt", "w", encoding="utf-8") as file:
    for entry in feed.entries:
        file.write(str(entry) + "\n\n")
    
    
## This gives better results with pprint. 
## Actually useable info for route filtering
with open("test/oc_rss_feed2.txt", "w", encoding="utf-8") as file:
    for entry in feed.entries:
        file.write(pprint.pformat(entry) + "\n\n")
