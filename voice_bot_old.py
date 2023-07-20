import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

import os
import datetime
import pymongo


db_name = 'interviews'
coll_name = 'testing'

test_client = pymongo.MongoClient('mongodb://localhost:27017/')

db = test_client[db_name]
collection = db[coll_name]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

Q1, ANSWER, FINISH, PROID, CHECK_ID,INTRO = range(6)

questions = [
            "What are your favorite things to do in your free time?",
            "What characteristics of yourself are you most proud of?",
            "What is your most common sexual fantasy?",
            "What have you done in your life that you feel most guilty about?"
        ]


def start(update: Update, context: CallbackContext) -> int:
    #id = collection.count_documents({}) + 1
    #collection.insert_one({'_id': id})

    context.user_data['step'] = -1
    #context.user_data['id'] = id

    reply_keyboard = [["Let's start!"]]
    update.message.reply_text("This is a start message",
    reply_markup = ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Next Question?'
        ),
    )

    return PROID

def prolific(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Please write your Prolific ID")
    return CHECK_ID

def wrongid(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
"""
Looks like you don't know your Prolific ID!
for test purposes enter this id:
5a9d64f5f6dfdd0001eaa73d
""")

    return CHECK_ID


def intro(update: Update, context: CallbackContext) -> int:
    context.user_data["proid"] = update.message.text
    collection.insert_one({'Prolific ID': context.user_data["proid"],
                           'type': 'text'})

    reply_keyboard = [["Got it!"]]

    update.message.reply_text("Description of the study",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Let's start?"
        ),
    )
    return INTRO

def q1(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Next Question']]

    print(context.user_data['step'])
    context.user_data['step'] += 1

    #print(update.message.text)
    #collection.update_one({'_id': id}, {'$push': {'valuable_things': response}})

    update.message.reply_text(questions[context.user_data['step']]
        ,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Next Question?'
        ),
    )

    if context.user_data['step'] == 3:
        return FINISH
    else:
        return Q1

def answer(update: Update, context: CallbackContext) -> int:
    q = 'Q' + str((context.user_data['step'] + 1))

    #collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {q: update.message.text}})
    new_file = context.bot.get_file(update.message.voice.file_id)

    fol_name = str(update.message.chat_id)
    if not os.path.exists(fol_name):
        os.mkdir(fol_name)

    path = f"{fol_name}/{q} - {datetime.datetime.now()}.ogg"
    new_file.download(path)
    collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {q: path}})

    return Q1

def finish(update: Update, context: CallbackContext) -> int:
    # q = 'Q' + str((context.user_data['step'] + 1))
    #collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {q: 'test'}})

    new_file = context.bot.get_file(update.message.voice.file_id)

    print(update.message)

    fol_name = str(update.message.chat_id)
    if not os.path.exists(fol_name):
        os.mkdir(fol_name)
    path = f"{fol_name}/{q} - {datetime.datetime.now()}.ogg"
    new_file.download(path)

    collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {q: path}})

    reply_keyboard = [['Okay, Bye!']]
    update.message.reply_text(
        '''Thank you! Here is your completion code:

I2PWSFRG''',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Next Question?'
        ),
    )

    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN ID")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher


 #)
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            CHECK_ID: [MessageHandler(Filters.regex("\w{24}"), intro),MessageHandler(Filters.text,wrongid)],
            PROID: [MessageHandler(Filters.text, prolific, pass_user_data=True)],
            INTRO: [MessageHandler(Filters.text, q1, pass_user_data=True)],
            Q1: [MessageHandler(Filters.regex('^Next Question$'), q1, pass_user_data=True), MessageHandler(Filters.text | Filters.voice, answer, pass_user_data=True)],
            FINISH: [MessageHandler(Filters.text, finish, pass_user_data=True)],
            #VOICE: MessageHandler(Filters.voice,answer)
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()