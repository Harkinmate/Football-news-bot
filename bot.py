import feedparser
import requests
import json
import os
from bs4 import BeautifulSoup
from telegram import Bot

# Your bot token & channel
BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHANNEL_ID = "@football1805"

# BBC Football RSS
RSS_URL = "http://feeds.bbci.co.uk/sport/football/rss.xml"

# Cache file for posted links
CACHE_FILE = "posted.json"


def load_posted():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_posted(posted):
    with open(CACHE_FILE, "w") as f:
        json.dump(list(posted), f)


def get_news():
    feed = feedparser.parse(RSS_URL)
    articles = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        summary = BeautifulSoup(entry.summary, "html.parser").get_text()

        # Try to extract image from media_content or summary
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0].get("url", None)
        else:
            soup = BeautifulSoup(entry.summary, "html.parser")
            img = soup.find("img")
            if img:
                image_url = img["src"]

        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "image": image_url
        })
    return articles


def main():
    bot = Bot(token=BOT_TOKEN)
    posted = load_posted()
    news = get_news()

    count = 0
    for article in news[:5]:  # take top 5 per run
        if article["link"] not in posted:
            msg = f"⚽ <b>{article['title']}</b>\n\n{article['summary']}\n\n🔗 {article['link']}"
            if article["image"]:
                bot.send_photo(chat_id=CHANNEL_ID, photo=article["image"], caption=msg, parse_mode="HTML")
            else:
                bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="HTML")

            posted.add(article["link"])
            count += 1
            if count >= 5:
                break

    save_posted(posted)


if __name__ == "__main__":
    main()
