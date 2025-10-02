import feedparser
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import time

# === CONFIG ===
API_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHAT_ID = "@football1805"
FEED_URL = "http://feeds.bbci.co.uk/sport/football/rss.xml"
CHECK_INTERVAL = 300  # 5 minutes

bot = Bot(token=API_TOKEN)
posted_links = []

def fetch_news():
    feed = feedparser.parse(FEED_URL)
    return feed.entries[:5]

def get_full_image(article_url):
    """Try to scrape the main image from the article page"""
    try:
        r = requests.get(article_url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # BBC usually stores main image in <meta property="og:image">
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]

    except Exception as e:
        print("Image fetch error:", e)
    return None

def send_news():
    global posted_links
    entries = fetch_news()

    for entry in reversed(entries):
        if entry.link not in posted_links:
            title = entry.title
            summary = entry.summary if hasattr(entry, "summary") else ""
            text = f"⚽ <b>{title}</b>\n\n{summary}"

            # Get big image from article page
            image_url = get_full_image(entry.link)

            try:
                if image_url:
                    bot.send_photo(chat_id=CHAT_ID, photo=image_url, caption=text, parse_mode="HTML")
                else:
                    bot.send_message(chat_id=CHAT_ID, text=text, parse_mode="HTML")
                print(f"Posted: {title}")
            except Exception as e:
                print("Send error:", e)

            posted_links.append(entry.link)
            if len(posted_links) > 100:
                posted_links = posted_links[-100:]

def main():
    while True:
        send_news()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
