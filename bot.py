import feedparser
import requests
import html
import time

# === CONFIG ===
BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHAT_ID = "@football1805"   # Channel username with @
FEED_URL = "http://feeds.bbci.co.uk/sport/football/rss.xml"

def fetch_and_send():
    print("🚀 Bot started")

    # Parse the RSS feed
    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        print("⚠️ No entries found in feed.")
        return

    print(f"✅ Fetched {len(feed.entries)} articles")

    # Take only the first (latest) entry
    entry = feed.entries[0]
    title = html.unescape(entry.title)
    summary = html.unescape(entry.summary) if "summary" in entry else ""
    link = entry.link

    # Try to get image
    image_url = None
    if "media_content" in entry:
        image_url = entry.media_content[0]["url"]
    elif "links" in entry:
        for link_data in entry.links:
            if link_data.get("type", "").startswith("image"):
                image_url = link_data["href"]
                break

    message_text = f"📌 <b>{title}</b>\n\n{summary}"

    print(f"⚽ Sending: {title}")

    if image_url:
        send_photo(image_url, message_text)
    else:
        send_message(message_text)

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
