import logging
from telegram.ext import (Updater, InlineQueryHandler, CommandHandler,  CallbackQueryHandler, MessageHandler, Filters, ConversationHandler, CallbackContext)
from telegram.ext.dispatcher import run_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import requests
import re
import psycopg2
from psycopg2 import Error
import random
import logging
import os
import math
import time
import datetime
from array import array

PORT = int(os.environ.get('PORT', 5000))
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '1908824393:AAE3SZKfsySMCu-PZQNqtuiy7Xm4GXKEHsM'

given_keyboard = [['CREATE Deck', 'VIEW deck 👀'],
                  ['ADD Deck ➕', 'DELETE deck ⛔'],
                  ['PRACTICE 💪', 'TEST ✍'],
                  ['COMPETE']]

markup = ReplyKeyboardMarkup(given_keyboard)


def connect_db():
    connection = psycopg2.connect(user="ypuzvnpikuyzec",
                                  password="b508ea454fb3ea5f4831560152799b203714bc742bb8c4b000fac6b91ef28cec",
                                  host="ec2-35-171-31-33.compute-1.amazonaws.com",
                                  port="5432",
                                  database="dfhns0og19dacd")
    return connection


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    startMessage = "Click NEW to get started!\n\n"
    startMessage += "Need help? 🆘\nClick /help to see all available commands and what they do.\n"
    update.message.reply_text(startMessage, reply_markup=markup)
    try:
        connection = connect_db()
        cursor = connection.cursor()
        postgres_insert_query = """INSERT INTO users (user_id, users_questions, test_done) VALUES (%s, %s, False) """
        user_to_insert = (getID(update), [],)
        cursor.execute(postgres_insert_query, user_to_insert)
        connection.commit()
        count = cursor.rowcount
        print (count, "user inserted successfully into users table")
    except (Exception, psycopg2.Error):# as error :
        if (connection):
            # print("Failed to insert user into users table: ", error)
            print("User already registered")
    finally:
        if (connection):
            cursor.close()
            connection.close()
            # print("PostgreSQL connection is closed")

def getID(update):
    return(update.message.chat.id)


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    start()

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)

    updater.bot.setWebhook('https://lifehackbots.herokuapp.com/' + TOKEN)
    updater.idle()

if __name__ == '__main__':
    main()