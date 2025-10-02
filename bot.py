import feedparser
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import hashlib
import json
import os
from bs4 import BeautifulSoup
import random

# ===== CONFIG =====
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
FEED_URL = "https://feeds.bbci.co.uk/sport/football/rss.xml"
POSTED_FILE = "posted.json"
MAX_POSTS_PER_RUN = 5

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Load posted content IDs
if os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "r") as f:
        posted = json.load(f)
else:
    posted = []

def generate_post_id(title, link):
    return hashlib.md5(f"{title}-{link}".encode()).hexdigest()

def generate_hashtags(entry):
    tags = []
    if "category" in entry:
        tags = [entry.category.replace(" ", "")]
    return " ".join(f"#{tag}" for tag in tags) or "#Football"

def clean_html(content):
    return BeautifulSoup(content, "html.parser").get_text()

def create_message(entry):
    full_content = entry.get("content")[0]["value"] if "content" in entry else entry.summary
    full_content = clean_html(full_content)
    words = full_content.split()
    if len(words) > 70:
        preview = " ".join(words[:70]) + "..."
        remaining = " ".join(words[70:])
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("Read Full Content", callback_data=remaining)
        ]])
        message_text = f'“{entry.title}”\n\n{preview}\n\n{generate_hashtags(entry)}'
        return message_text, keyboard
    else:
        message_text = f'“{entry.title}”\n\n{full_content}\n\n{generate_hashtags(entry)}'
        return message_text, None

# Fetch RSS feed
feed = feedparser.parse(FEED_URL)
new_entries = [entry for entry in feed.entries if generate_post_id(entry.title, entry.link) not in posted]

# Shuffle and pick up to MAX_POSTS_PER_RUN
random.shuffle(new_entries)
entries_to_post = new_entries[:MAX_POSTS_PER_RUN]

for entry in entries_to_post:
    post_id = generate_post_id(entry.title, entry.link)
    message_text, keyboard = create_message(entry)

    # Attempt to get image from media content
    image_url = None
    if "media_content" in entry:
        image_url = entry.media_content[0]["url"]
    elif "media_thumbnail" in entry:
        image_url = entry.media_thumbnail[0]["url"]

    try:
        if image_url:
            bot.send_photo(
                chat_id=TELEGRAM_CHANNEL_ID,
                photo=image_url,
                caption=message_text,
                reply_markup=keyboard
            )
        else:
            bot.send_message(
                chat_id=TELEGRAM_CHANNEL_ID,
                text=message_text,
                reply_markup=keyboard
            )
        posted.append(post_id)
        with open(POSTED_FILE, "w") as f:
            json.dump(posted, f)
    except Exception as e:
        print(f"Error posting: {e}")

# ===== CALLBACK HANDLER =====
from telegram.ext import Updater, CallbackQueryHandler

def button_callback(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=query.data)

updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
updater.dispatcher.add_handler(CallbackQueryHandler(button_callback))
updater.start_polling()
updater.idle()
