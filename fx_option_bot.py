import time  # <-- this line
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import os
import logging
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import telebot
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = '7570116431:AAHOQ16QJWB1ZpwuisCYoJp9YjInHCDy2RA'
CHANNEL_ID = '@serialtradersfx'
FOREX_URL = 'https://www.forexlive.com/orders'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Initialize Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)

def get_target_article():
    """Fetch and parse the target article from ForexLive"""
    try:
        response = requests.get(FOREX_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all articles (adjust selector based on actual page structure)
        articles = soup.find_all('article', limit=5)
        
        for article in articles:
            title_tag = article.find('h2', class_='title')
            if title_tag and title_tag.text.strip().startswith('FX option expiries for'):
                return article
        return None
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        return None

def extract_image(article):
    """Extract first image URL from article"""
    try:
        img_tag = article.find('img')
        return img_tag['src'] if img_tag and img_tag.has_attr('src') else None
    except Exception as e:
        logger.error(f"Error extracting image: {str(e)}")
        return None

def format_data(article):
    """Extract and format article data creatively"""
    try:
        # Extract date from title
        title = article.find('h2', class_='title').text.strip()
        date_str = title.replace('FX option expiries for ', '')
        
        # Extract relevant content
        content = article.find('div', class_='article-content')
        if not content:
            return f"📅 {date_str}\n\nNo expiries data available today"
        
        # Create formatted message
        message = f"📊 *FX Option Expiries - {date_str}* 📊\n\n"
        message += "💵 *Major Currency Pairs Expiry Levels* 💵\n"
        
        # Example parsing (adjust based on actual content structure)
        items = content.find_all('p', limit=5)
        for item in items:
            text = item.get_text().strip()
            if 'EUR/USD' in text or 'USD/JPY' in text or 'GBP/USD' in text:
                message += f"➖ {text}\n"
        
        message += "\nℹ️ Full details available at ForexLive.com"
        return message
    except Exception as e:
        logger.error(f"Error formatting data: {str(e)}")
        return "⚠️ Data format changed - Please check manually"

def post_to_telegram(image_url=None, message=None):
    """Post content to Telegram channel"""
    try:
        if image_url:
            # Download and send image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            with open('temp_image.jpg', 'wb') as f:
                for chunk in response:
                    f.write(chunk)
            
            with open('temp_image.jpg', 'rb') as photo:
                bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=photo,
                    caption=message[:200] if message else '',
                    parse_mode='Markdown'
                )
            os.remove('temp_image.jpg')
            return True
        elif message:
            bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode='Markdown'
            )
            return True
        return False
    except Exception as e:
        logger.error(f"Telegram post failed: {str(e)}")
        return False

def daily_task():
    """Main task to execute daily"""
    logger.info("Starting daily FX options update...")
    
    article = get_target_article()
    if not article:
        post_to_telegram(message="⚠️ No FX options article found today")
        return
    
    # Try to post image first
    image_url = extract_image(article)
    success = False
    
    if image_url:
        formatted_data = format_data(article)
        success = post_to_telegram(image_url=image_url, message=formatted_data)
    
    # Fallback to text message if image fails
    if not success:
        formatted_data = format_data(article)
        post_to_telegram(message=formatted_data)
    
    logger.info("Daily task completed")

def schedule_jobs():
    """Schedule daily task at 8:00 AM EAT"""
    scheduler = BackgroundScheduler(timezone=pytz.timezone('Africa/Nairobi'))
    scheduler.add_job(
        daily_task,
        trigger=CronTrigger(hour=8, minute=0),
        name='daily_fx_options_update'
    )
    
    try:
        scheduler.start()
        logger.info("Scheduler started. Waiting for jobs...")
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down")

if __name__ == '__main__':
    schedule_jobs()
