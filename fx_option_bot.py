import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os

# Telegram Setup
BOT_TOKEN = "7570116431:AAHOQ16QJWB1ZpwuisCYoJp9YjInHCDy2RA"
CHANNEL_ID = "@serialtradersfx"
bot = Bot(token=BOT_TOKEN)

def get_latest_article_url():
    url = "https://www.forexlive.com/Orders"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    article = soup.find("article")
    if article:
        link = article.find("a")["href"]
        return link
    return None

def download_expiry_chart(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Look for the first image inside the article (usually the expiry chart)
    image = soup.find("img", {"src": lambda x: x and "forexlive" in x})
    if image:
        image_url = image["src"]
        img_data = requests.get(image_url).content
        image_path = "fx_expiry_chart.png"
        with open(image_path, "wb") as f:
            f.write(img_data)
        return image_path
    return None

def send_to_telegram(image_path):
    with open(image_path, "rb") as img:
        bot.send_photo(chat_id=CHANNEL_ID, photo=img, caption="Latest FX Option Expiry Chart")

def main():
    article_url = get_latest_article_url()
    if article_url:
        image_path = download_expiry_chart(article_url)
        if image_path:
            send_to_telegram(image_path)
            print("Image sent successfully.")
        else:
            print("No image found in the article.")
    else:
        print("No latest article found.")
    else:
    print("Found article URL:",article_url)
else:
    print("Downloaded image path:",image_path)
          
          if __name__ == "__main__":
    main()
