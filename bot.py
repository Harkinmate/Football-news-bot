import feedparser
import hashlib
import json
import os
import random
from bs4 import BeautifulSoup
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
from telegram import Update

# ===== CONFIG =====
TELEGRAM_BOT_TOKEN = "7839637427:AAE0LL7xeUVJiJusSHaHTOGYAI3kopwxdn4"
TELEGRAM_CHANNEL_ID = "@football1805"
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

async def post_feed(context: ContextTypes.DEFAULT_TYPE):
    feed = feedparser.parse(FEED_URL)
    new_entries = [entry for entry in feed.entries if generate_post_id(entry.title, entry.link) not in posted]

    random.shuffle(new_entries)
    entries_to_post = new_entries[:MAX_POSTS_PER_RUN]

    for entry in entries_to_post:
        post_id = generate_post_id(entry.title, entry.link)
        message_text, keyboard = create_message(entry)

        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0]["url"]
        elif "media_thumbnail" in entry:
            image_url = entry.media_thumbnail[0]["url"]

        try:
            if image_url:
                await context.bot.send_photo(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    photo=image_url,
                    caption=message_text,
                    reply_markup=keyboard
                )
            else:
                await context.bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=message_text,
                    reply_markup=keyboard
                )
            posted.append(post_id)
            with open(POSTED_FILE, "w") as f:
                json.dump(posted, f)
        except Exception as e:
            print(f"Error posting: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=query.data)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CallbackQueryHandler(button_callback))
    app.job_queue.run_repeating(post_feed, interval=1800, first=0)  # every 30 mins
    app.run_polling()
