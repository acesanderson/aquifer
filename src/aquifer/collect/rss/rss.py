import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import feedparser  # pip install feedparser


# Method 1: Raw requests + XML parsing (educational)
def parse_rss_manual(url):
    response = requests.get(url, headers={"User-Agent": "Aquifer/1.0"})
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = []

    for item in root.findall(".//item"):
        title = (
            item.find("title").text if item.find("title") is not None else "No title"
        )
        link = item.find("link").text if item.find("link") is not None else ""
        description = (
            item.find("description").text
            if item.find("description") is not None
            else ""
        )
        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""

        items.append(
            {
                "title": title,
                "link": link,
                "description": description,
                "published": pub_date,
            }
        )

    return items


# Method 2: Using feedparser (recommended)
def parse_rss_feedparser(url):
    feed = feedparser.parse(url)

    if feed.bozo:  # Indicates parsing errors
        print(f"Warning: Feed parsing issues for {url}")

    items = []
    for entry in feed.entries:
        items.append(
            {
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "description": entry.get("summary", entry.get("description", "")),
                "published": entry.get("published", ""),
                "published_parsed": entry.get("published_parsed"),  # struct_time object
                "author": entry.get("author", ""),
            }
        )

    return {
        "feed_title": feed.feed.get("title", "Unknown"),
        "feed_description": feed.feed.get("description", ""),
        "items": items,
    }


# Example usage
if __name__ == "__main__":
    # Test with a reliable RSS feed
    # url = "https://www.edsurge.com/articles_rss"
    url = "https://newsletters.qs.com/rss/"

    try:
        result = parse_rss_feedparser(url)
        print(f"Feed: {result['feed_title']}")
        print(f"Latest items: {len(result['items'])}")

        for item in result["items"][:10]:  # Show first 3
            print(f"\nTitle: {item['title']}")
            print(f"Published: {item['published']}")
            print(f"Link: {item['link']}")

    except Exception as e:
        print(f"Error: {e}")
