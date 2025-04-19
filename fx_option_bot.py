import requests
from bs4 import BeautifulSoup
import telegram
from datetime import datetime

# Your Telegram bot credentials
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHANNEL_ID = "@serialtradersfx"

bot = telegram.Bot(token=BOT_TOKEN)

def get_fx_expiry_data():
    url = "https://www.forexlive.com/technical-analysis/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = soup.find_all("article")
    expiry_data = ""

    for article in articles:
        title = article.find("h2")
        if title and "option expiry" in title.get_text().lower():
            link = article.find("a")["href"]
            article_page = requests.get(link)
            article_soup = BeautifulSoup(article_page.text, "html.parser")
            content = article_soup.find("div", class_="single-post-content")

            if content:
                lines = content.get_text(separator="\n").splitlines()
                for line in lines:
                    if any(pair in line for pair in ["EUR/USD", "USD/JPY", "GBP/JPY"]):
                        expiry_data += line.strip() + "\n"
            break

    return expiry_data or "No expiry data found today."

def send_expiry_to_telegram():
    data = get_fx_expiry_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = f"*FX Option Expiries — {now}*\n\n`{data}`"
    bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=telegram.ParseMode.MARKDOWN)

send_expiry_to_telegram()
