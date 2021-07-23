import logging
import os
import random
import psycopg2
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

CHOOSING, CREATE_DECK, CREATE_ANSWERS, CREATE_QUESTIONS, PLAY_DECK, VIEW_ALL_DECKS, VIEW_MY_DECKS, LEADERBOARDS, \
MOTIVATION = range(9)

PORT = int(os.environ.get('PORT', 5000))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '1908824393:AAE3SZKfsySMCu-PZQNqtuiy7Xm4GXKEHsM'

reply_keyboard = [['Create Deck', 'Play Deck'],
                  ['View All Decks', 'View My Decks'],
                  ['Leaderboards', 'Motivate Me!']]

markup = ReplyKeyboardMarkup(reply_keyboard)


def generate_random_string():
    deck_token = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
    return deck_token


def database_connection():
    con = psycopg2.connect(user="wphtrnjifgtphq",
                           password="c870974f40f5ca10d7f7abcb6cbc4b89137bc612a516a917784990da74c3bd95",
                           host="ec2-35-174-56-18.compute-1.amazonaws.com",
                           port="5432",
                           database="dac876p6jjg42g")
    return con


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    start_message = "Welcome to LifeHack Bot! \n\nNeed help? Click /help to see all available commands and what they do."
    update.message.reply_text(start_message, reply_markup=markup)
    return CHOOSING


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def create_deck_message(update, context):
    update.message.reply_text(
        "Want to create a new deck? Please give your new deck a name. \n\nTo cancel, type /cancel.")
    return CREATE_DECK


def create_deck(update, context):
    user_input = update.message.text
    deck_token = generate_random_string()
    if user_input == "/cancel":
        cancel(update, context)
        return CHOOSING
    else:
        deck = user_input
        try:
            connection = database_connection()
            cursor = connection.cursor()
            deck_data = (user_input, "hi all", deck_token)
            insert_query = """INSERT INTO decks (deck_name, deck_owner, deck_token) VALUES (%s, %s, %s) """
            cursor.execute(insert_query, deck_data)
            connection.commit()
            print("Deck created successfully!")
        except (Exception, psycopg2.Error) as e:  # as error :
            print(format(e))
        finally:
            if (connection):
                cursor.close()
                connection.close()
    return CREATE_QUESTIONS


def create_questions(update, context):
    print("qn")
    if update.message.text == "/submit":
        cancel(update, context)
        return CHOOSING
    else:
        update.message.reply_text("Please enter your question")
        return CREATE_ANSWERS


def create_answers(update, context):
    if update.message.text == "/submit":
        cancel(update, context)
        return CHOOSING
    else:
        update.message.reply_text("Please enter your answers")
        return CREATE_QUESTIONS


def play_deck_message(update, context):
    update.message.reply_text("Enter deck token to play!. \n\nTo cancel, type /cancel.")
    return PLAY_DECK


def play_deck(update, context):
    user_input = update.message.text
    if (user_input == "/cancel"):
        cancel(update, context)
        return CHOOSING
    else:
        update.message.reply_text(user_input)  # echo -> Si Ting TODO
    return CHOOSING


def view_all_decks_message(update, context):
    update.message.reply_text("Here are all available decks. Enter a deck token to play! \n\nTo cancel, type /cancel.")
    return PLAY_DECK


def view_my_decks_message(update, context):
    update.message.reply_text("Drk what to do here @ST Enter token to view leaderboards? To play?")
    return CHOOSING


def cancel(update, context):
    update.message.reply_text("Cancelled!", reply_markup=markup)
    return CHOOSING


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def done(update, context):
    update.message.reply_text("Thanks for playing! Come back soon!")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("help", help))

    # handle button press
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('Create Deck'), create_deck_message),
                MessageHandler(Filters.regex('Play Deck'), play_deck_message),
                MessageHandler(Filters.regex('View All Decks'), view_all_decks_message),
                MessageHandler(Filters.regex('View My Decks'), view_my_decks_message)

            ],
            CREATE_DECK: [MessageHandler(Filters.text, create_deck)],
            PLAY_DECK: [MessageHandler(Filters.text, play_deck)],
            CREATE_QUESTIONS: [MessageHandler(Filters.text, create_questions)],
            CREATE_ANSWERS: [MessageHandler(Filters.text, create_answers)]
        },
        fallbacks=[CommandHandler('done', done)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)
    updater.start_polling()

    # updater.start_webhook(listen="0.0.0.0",
    #                      port=int(PORT),
    #                     url_path=TOKEN)
    # updater.bot.setWebhook('https://lifehackbots.herokuapp.com/' + TOKEN)

    # updater.idle()


if __name__ == '__main__':
    main()
