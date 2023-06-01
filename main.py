import os
import logging
import schedule
import time
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token from environment variable
TOKEN = os.getenv("6043054287:AAGwCMEOTcY0d7N-s8JtnQ9HUFYOQG-pWzQ")

# IMDb news website URL
NEWS_URL = "https://www.imdb.com/news"  # Replace with the actual IMDb news website URL

def start(update: Update, context: CallbackContext):
    """Handler for /start command"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the IMDb News Bot!\nSend /news to get the latest IMDb news updates.")

def news(update: Update, context: CallbackContext):
    """Handler for /news command"""
    # Send a typing action while fetching the news
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="TYPING")

    # Fetch the latest IMDb news
    news_items = fetch_imdb_news()

    if news_items:
        # Send each news item as a separate message
        for news_item in news_items:
            context.bot.send_message(chat_id=update.effective_chat.id, text=news_item)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No IMDb news found.")

def fetch_imdb_news():
    """Fetch the latest IMDb news from the website"""
    # Make a request to the IMDb news website
    response = requests.get(NEWS_URL)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        news_items = soup.find_all("div", class_="news-article")

        # Extract the news headlines
        headlines = [item.find("a").text for item in news_items]

        return headlines

    return None

def auto_send_news(context: CallbackContext):
    """Function to auto-send news updates"""
    news_items = fetch_imdb_news()

    if news_items:
        for news_item in news_items:
            context.bot.send_message(chat_id=context.job.context, text=news_item)

def error(update: Update, context: CallbackContext):
    """Log errors"""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Main function to start the bot"""
    # Create the Updater and pass in the bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("news", news))

    # Register error handler
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()

    # Schedule auto-send news updates every 24 hours
    job_queue = updater.job_queue
    job_queue.run_repeating(auto_send_news, interval=86400, context=updater.bot.get_me().id)

    # Run the bot
    updater.idle()

if __name__ == '__main__':
    main()
