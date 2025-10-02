import requests
from bs4 import BeautifulSoup
import feedparser
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID", "@football1805")

BBC_RSS = "http://feeds.bbci.co.uk/sport/football/rss.xml"

posted = set()

def send_to_telegram(title, summary, image_url=None):
    if image_url:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "caption": f"{title}\n\n{summary}"[:1024]},
            files={"photo": requests.get(image_url).content},
        )
    else:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": f"{title}\n\n{summary}"[:4096]},
        )

def fetch_bbc():
    feed = feedparser.parse(BBC_RSS)
    for entry in feed.entries:
        if entry.id in posted:
            continue
        title = entry.title
        summary = entry.summary if hasattr(entry, "summary") else ""
        image_url = None
        if "media_content" in entry:
            image_url = entry.media_content[0]["url"]
        send_to_telegram(title, summary, image_url)
        posted.add(entry.id)
        break

def fetch_talksport():
    url = "https://talksport.com/football/"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    article = soup.find("article")
    if not article:
        return

    link = article.find("a")["href"]
    if link in posted:
        return

    title = article.find("h3").get_text(strip=True)
    image_tag = article.find("img")
    image_url = image_tag["src"] if image_tag else None
    summary = article.find("p").get_text(strip=True) if article.find("p") else ""

    send_to_telegram(title, summary, image_url)
    posted.add(link)

if __name__ == "__main__":
    fetch_bbc()
    fetch_talksport()
