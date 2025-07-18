import feedparser
import html
import gzip
import re
import ssl
import sys
import urllib.request
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Ignore SSL warnings

def convert(html_text):
    # Decode HTML s-strings
    text = html.unescape(html_text)
    
    # Convert to rich markup
    replacements = [
        (r'<(?:strong|b)>(.*?)</(?:strong|b)>', r'[bold]\1[/bold]'),
        (r'<(?:em|i)>(.*?)</(?:em|i)>', r'[italic]\1[/italic]'),
        (r'<p>(.*?)</p>', r'\1\n'),
        (r'<[^>]+>', ''),  # Remove remaining HTML tags
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)
    re.sub(r'\n\s*\n', '\n\n', text.strip())  # Clean up whitespace
    
    return re.sub(r'\[/?(bold|italic|underline|dim|green|cyan|.*?)]', '', text)

# Set up custom headers to mimic a browser request with SSL context
https_handler = urllib.request.HTTPSHandler(context=ssl._create_unverified_context())
opener = urllib.request.build_opener(https_handler)
opener.addheaders = [
    ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
    ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'), ('Accept-Language', 'en-US,en;q=0.5'),
    ('Accept-Encoding', 'gzip, deflate'), ('Connection', 'keep-alive'), ('Upgrade-Insecure-Requests', '1')
    ]
urllib.request.install_opener(opener)

def parse_feed():
    try:
        response = urllib.request.urlopen("https://www.octranspo.com/feeds/updates-en/")
        rss_content = response.read()
        
        # Check if content is gzip compressed and decompress if needed
        content_encoding = response.getheader('Content-Encoding', '').lower()
        if content_encoding == 'gzip' or rss_content.startswith(b'\x1f\x8b'):
            rss_content = gzip.decompress(rss_content)
        
        # Parse the RSS content with feedparser
        feed = feedparser.parse(rss_content)
            
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return []

    # Check if the feed has entries
    if not feed.entries:
        print("No updates found in the feed.")
        return []

    entries = []
    if len(sys.argv) > 1:
    	limit = int(sys.argv[1])
    else: 
        limit = 5
    for entry in feed.entries[:limit]:  # Limit to first 5 entries
        update = {
            "title": entry.get("title", "No title"),
            "link": entry.get("link", "No link"),
            "published": entry.get("published", "No published date"),
            "description": entry.get("description", "No description available"),  # Keep raw HTML
            "categories": [entry.get("category")]
        }
        entries.append(update)

    return entries

if __name__ == "__main__":
    updates = parse_feed()

    if updates:
        print(f"Found {len(updates)} updates:")
        for update in updates:
            print("\n--- Update ---")
            print(f"Title: {update['title']}")
            print(f"Link: {update['link']}")
            print(f"Published: {update['published']}")
            print(f"Categories: {update['categories']}")
            
            # Format and display the description with HTML formatting applied
            print("Description:")
            print(convert(update["description"]))
    else:
        print("No new updates found.")
