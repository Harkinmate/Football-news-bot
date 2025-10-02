import feedparser
import requests
import os
import time
from datetime import datetime

# ---------------- CONFIG ----------------
BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
CHANNEL_ID = "@football1805"
RSS_FEED_URL = "http://feeds.bbci.co.uk/sport/football/rss.xml"
SENT_POSTS_FILE = "sent_posts.txt"
FETCH_INTERVAL = 60  # 1 minute
POSTS_PER_RUN = 3    # can set 2–5
# ----------------------------------------

def load_sent_posts():
    if os.path.exists(SENT_POSTS_FILE):
        with open(SENT_POSTS_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent_posts(sent_posts):
    with open(SENT_POSTS_FILE, "w") as f:
        for post_id in sent_posts:
            f.write(post_id + "\n")

def fetch_new_posts():
    sent_posts = load_sent_posts()
    feed = feedparser.parse(RSS_FEED_URL)
    
    today = datetime.utcnow().date()
    new_posts = []

    for entry in feed.entries:
        post_id = entry.id if 'id' in entry else entry.link
        published_date = datetime(*entry.published_parsed[:6]).date()
        if post_id not in sent_posts and published_date == today:
            # Get image from media content if available
            image_url = ""
            if 'media_content' in entry:
                image_url = entry.media_content[0]['url']
            new_posts.append((post_id, entry.title, entry.summary, image_url))
    
    # If no new posts today, consider last posts anyway to avoid empty
    if not new_posts:
        for entry in feed.entries:
            post_id = entry.id if 'id' in entry else entry.link
            if post_id not in sent_posts:
                image_url = ""
                if 'media_content' in entry:
                    image_url = entry.media_content[0]['url']
                new_posts.append((post_id, entry.title, entry.summary, image_url))

    return new_posts[-POSTS_PER_RUN:]  # last N posts

def send_posts(posts):
    sent_posts = load_sent_posts()
    for post_id, title, summary, image_url in posts:
        caption = f"*{title}*\n\n{summary}"
        try:
            if image_url:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                payload = {
                    "chat_id": CHANNEL_ID,
                    "photo": image_url,
                    "caption": caption,
                    "parse_mode": "Markdown"
                }
                requests.post(url, data=payload)
            else:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": CHANNEL_ID,
                    "text": caption,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": True
                }
                requests.post(url, data=payload)
            sent_posts.add(post_id)
        except Exception as e:
            print(f"Failed to send post {post_id}: {e}")
    save_sent_posts(sent_posts)

# Run continuously
while True:
    try:
        posts_to_send = fetch_new_posts()
        if posts_to_send:
            send_posts(posts_to_send)
        else:
            print("No new posts to send at this time.")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(FETCH_INTERVAL)
