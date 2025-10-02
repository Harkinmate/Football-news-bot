import feedparser
import requests
import html
import os

# === CONFIG ===
BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHAT_ID = "@football1805"   # Channel username with @
FEED_URL = "http://feeds.bbci.co.uk/sport/football/rss.xml"
LAST_POST_FILE = "last_posted.txt"

def get_last_posted():
    if os.path.exists(LAST_POST_FILE):
        with open(LAST_POST_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def set_last_posted(link):
    with open(LAST_POST_FILE, "w", encoding="utf-8") as f:
        f.write(link)

def fetch_and_send():
    print("🚀 Bot started")

    feed = feedparser.parse(FEED_URL)
    if not feed.entries:
        print("⚠️ No entries found in feed.")
        return

    print(f"✅ Fetched {len(feed.entries)} articles")

    last_posted = get_last_posted()
    new_posts = []

    # Collect new articles
    for entry in feed.entries[:5]:  # look at latest 5
        if entry.link == last_posted:
            break
        new_posts.append(entry)

    # Reverse so oldest new goes first
    new_posts.reverse()

    if not new_posts:
        print("⏸️ No new posts to send")
        return

    for entry in new_posts:
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

        message_text = f"⚽ <b>{title}</b>\n\n{summary}\n\n🔗 {entry.link}"

        print(f"📰 Sending: {title}")
        if image_url:
            send_photo(image_url, message_text)
        else:
            send_message(message_text)

    # Save the latest one
    set_last_posted(new_posts[-1].link)

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
