import feedparser
import requests
import html
import os

# === CONFIG ===
BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHAT_ID = "@football1805"   # Channel username with @
FEEDS = [
    "http://feeds.bbci.co.uk/sport/football/rss.xml",
    "https://talksport.com/feed/football/"
]
LAST_POST_FILE = "last_posted.txt"


def get_last_posted():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip().splitlines()
    return []


def set_last_posted(latest_links):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(latest_links))


def upgrade_image_url(url: str) -> str:
    """Try to get higher quality BBC/TalkSport images"""
    if url:
        return url.replace("/240/", "/976/").replace("/320/", "/976/")
    return url


def fetch_and_send():
    print("🚀 Bot started")

    last_posted_links = get_last_posted()
    all_new_posts = []
    latest_seen_links = []

    for feed_url in FEEDS:
        print(f"📡 Checking feed: {feed_url}")
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("⚠️ No entries found")
            continue

        new_posts = []
        for entry in feed.entries[:5]:  # only check top 5 per feed
            if entry.link in last_posted_links:
                break
            new_posts.append(entry)

        new_posts.reverse()  # oldest first
        all_new_posts.extend(new_posts)

        # Always track newest link from each feed
        latest_seen_links.append(feed.entries[0].link)

    if not all_new_posts:
        print("⏸️ No new posts across feeds")
        return

    for entry in all_new_posts:
        title = html.unescape(entry.title)
        summary = html.unescape(entry.summary) if "summary" in entry else ""
        image_url = None

        if "media_content" in entry:
            image_url = entry.media_content[0].get("url")
        elif "media_thumbnail" in entry:
            image_url = entry.media_thumbnail[0].get("url")
        elif "links" in entry:
            for link_data in entry.links:
                if link_data.get("type", "").startswith("image"):
                    image_url = link_data["href"]
                    break

        image_url = upgrade_image_url(image_url)

        message_text = f"📌 <b>{title}</b>\n\n{summary}"

        print(f"📰 Sending: {title}")
        if image_url:
            send_photo(image_url, message_text)
        else:
            send_message(message_text)

    # Save latest links from each feed
    set_last_posted(latest_seen_links)


def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    r = requests.post(url, json=payload)
    print("➡️ Message response:", r.text)


def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption,
        "parse_mode": "HTML"
    }
    r = requests.post(url, data=payload)
    print("➡️ Photo response:", r.text)


if __name__ == "__main__":
    fetch_and_send()
