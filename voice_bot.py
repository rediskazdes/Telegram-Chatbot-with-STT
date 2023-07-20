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

import re
import os
import datetime
import pymongo
import time
import secrets
import string

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

Q1, ANSWER, FINISH, CHECK_ID, INTRO, TRAIN1, TRAIN2,TRAIN_VOICE,INTRO_END = range(9)

questions = [
            "What are your favorite things to do in your free time? Please, try to provide details and examples",
            "What characteristics of yourself are you most proud of? Please, try to provide details and examples",
            "What has been the biggest disappointment in your life? Please, try to provide details and examples",
            "What characteristics of your best friend really bother you? Please, try to provide details and examples",
            "What is the OS of the computer you are using in this study?"
        ]

def start(update: Update, context: CallbackContext) -> int:
    context.user_data['step'] = 0

    #update.message.reply_text(
    #    """In this study, we gather a collection of responses to train a chatbot in understanding them and asking the follow-up questions. The chatbot is very simple — it only asks questions and stores your responses.  We need your help, so we can make it smarter.""")
    #time.sleep(3)
    #update.message.reply_text(
    #    """We ask you to respond as genuinely and detailed as possible. We also ask you to refrain from giving out any identifications (e.g. names or addresses).  This survey will take you approximately 20 minutes to complete. We will ask four questions about your personal life. You are free to omit any questions. You will be compensated for the given responses (1.5 euros per response). You can withdraw from the study at any given moment. In case of your withdrawal, we will not collect any data and you will not get compensated.""")
    #time.sleep(3)
    #update.message.reply_text(
    #    """To the best of our ability, responses in this study will remain confidential. We will keep it anonymous and will store it in a data repository with restricted access until the end of this Ph.D. project (2026). The data will be used for academic outputs (journals, publications, presentations) in a de-identified format.""")
    #time.sleep(3)
    #update.message.reply_text(
    #    """If you have questions or requests regarding your participation, feel free to contact d.bulygin@tudelft.nl . To give your consent and confirm you are legally able to give consent please enter your Prolific ID.""")
    #time.sleep(3)

    #alphabet = string.ascii_letters + string.digits
    #password = ''.join(secrets.choice(alphabet) for i in range(24))

    #reply_keyboard = [[password]]

    update.message.reply_text("Before we start the interview, please enter your Prolific ID"
                              #,
                              #reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
                              )
    return CHECK_ID

def wrongid(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        """
        Looks like you don't know your Prolific ID!
        for test purposes enter this id:
        5a9d64f5f6dfdd0001eaa73d
        """)

    return CHECK_ID

#def os_q(update: Update, context: CallbackContext) -> int:
#    context.user_data["proid"] = update.message.text
#    collection.insert_one({'Prolific ID': context.user_data["proid"],
#                           'type': 'voice'})

def train_voice(update: Update, context: CallbackContext) -> int:
    context.user_data["proid"] = update.message.text
    collection.insert_one({'Prolific ID': context.user_data["proid"],
                           'type': 'voice'})

    collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {'tut_start': datetime.datetime.utcnow()}})

    #update.message.reply_text("Before we get to the study, let's learn what you can do.")
    #time.sleep(1)
    update.message.reply_text("You can record the voice by clicking the icon of mic. Let's try to do it before we start the interview")
    time.sleep(1)
    update.message.reply_text(
        "Draw the mic to the locker and you are free to record yourself for as long as you want")
    update.message.reply_animation("https://thumbs.gfycat.com/TallDismalCleanerwrasse-size_restricted.gif")
    time.sleep(2)
    update.message.reply_text("To stop the recording just click the red circle")
    time.sleep(3)
    update.message.reply_text("""
Let's train to record your voice. For example:
    """)
    update.message.reply_text("""
How do you feel today?
        """)
    time.sleep(3)
    update.message.reply_text("""
Remember, I understand only voice recordings and button commands
            """)

    return TRAIN_VOICE

def train1(update: Update, context: CallbackContext) -> int:
    q = 'train_Q'
    q_t = str(q) + '_time'

    new_file = context.bot.get_file(update.message.voice.file_id)

    fol_name = rf'C:\Users\dbulygin\Dropbox\pythonProject\recordings\{str(context.user_data["proid"])}'

    if not os.path.exists(fol_name):
        os.mkdir(fol_name)

    path = rf'{fol_name}\{q}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.ogg'
    new_file.download(path)

    collection.update_one({'Prolific ID': context.user_data["proid"]},
                          {'$push': {q: path, q_t: datetime.datetime.utcnow()}})

    reply_keyboard = [["Next Question"]]

    update.message.reply_text("""
You can send as many voices to answer a question as you want. You'll move on to the next question only after you tap "Next Question"
    """, reply_markup=ReplyKeyboardMarkup(
                            reply_keyboard,resize_keyboard=True
                              ))
    return TRAIN1

def intro_end(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [["Let's start!"]]

#    collection.update_one({'Prolific ID': context.user_data["proid"]}, {'$push': {'train1': datetime.datetime.utcnow()}})
#
    update.message.reply_text("""
Great!
You submitted your voices to this training question. Let's start the main interview?
""",
    reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, resize_keyboard=True
    ))
    return INTRO_END

#def train2(update: Update, context: CallbackContext) -> int:
#    collection.update_one({'Prolific ID': context.user_data["proid"]},
#                          {'$push': {'train2': datetime.datetime.utcnow()}})
#
#
 #   reply_keyboard = [["Previous Question", "Next Question"]]
#
 #   update.message.reply_text("""
  #  How did you feel yesterday on the scale of 0 to 5?
   # """)
    #update.message.reply_text("""
#Yay! You are on the next question. You can always go back to the previous questions and add more information. Let's try and get back to the previous question.
#"""
#                              , reply_markup=ReplyKeyboardMarkup(
#                            reply_keyboard
#                              )
#                              )
#    return TRAIN2

#def train3(update: Update, context: CallbackContext) -> int:
#    collection.update_one({'Prolific ID': context.user_data["proid"]},
#                          {'$push': {'train3': datetime.datetime.utcnow()}})

#    reply_keyboard = [["Let's start"]]

#    update.message.reply_text("""
#How do you feel today on the scale of 0 to 5?
#"""
#)
#    time.sleep(2)
#    update.message.reply_text("""
#That's it! Let's start the interview?
#""",
#                              reply_markup=ReplyKeyboardMarkup(
#                                  reply_keyboard, one_time_keyboard=True
#                              ),
#                              )
#    return INTRO

def q1(update: Update, context: CallbackContext) -> int:

    collection.update_one({'Prolific ID': context.user_data["proid"]},
                          {'$push': {'train4': datetime.datetime.utcnow()}})

    if context.user_data['step'] == 4:
        reply_keyboard = [['Windows'],['MacOS'],['Other']]
    else:
        reply_keyboard = [['Next Question','Skip Question'], ['Withdraw from the study']]

    update.message.reply_text(questions[context.user_data['step']],
                              reply_markup=ReplyKeyboardMarkup(
                                  reply_keyboard, one_time_keyboard=True,resize_keyboard=True
                              ),
                              )

    context.user_data['step'] += 1
    print(context.user_data['step'])

    if context.user_data['step'] == 5:
        return FINISH
    else:
        return Q1

def answer(update: Update, context: CallbackContext) -> int:
    q = 'Q' + str((context.user_data['step']))
    q_t = str(q) + 'time'

    new_file = context.bot.get_file(update.message.voice.file_id)

    fol_name = rf'C:\Users\dbulygin\Dropbox\pythonProject\recordings\{str(context.user_data["proid"])}'

    if not os.path.exists(fol_name):
        os.mkdir(fol_name)

    path = rf'{fol_name}\{q}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.ogg'
    new_file.download(path)

    collection.update_one({'Prolific ID': context.user_data["proid"]},
                          {'$push': {q: path, q_t: datetime.datetime.utcnow()}})

    if context.user_data['step'] == 5:
        return FINISH
    else:
        return Q1

def finish(update: Update, context: CallbackContext) -> int:
    q = 'Q' + str((context.user_data['step']))
    q_t = str(q) + 'time'
    new_file = context.bot.get_file(update.message.voice.file_id)
    fol_name = rf'C:\Users\dbulygin\Dropbox\pythonProject\recordings\{str(context.user_data["proid"])}'
    if not os.path.exists(fol_name):
        os.mkdir(fol_name)

    path = rf'{fol_name}\{q}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.ogg'
    new_file.download(path)

    collection.update_one({'Prolific ID': context.user_data["proid"]},
                      {'$push': {q: path, q_t: datetime.datetime.utcnow()}})

    return FINISH

def finish1(update: Update, context: CallbackContext) -> int:
    collection.update_one({'Prolific ID': context.user_data["proid"]},{'$push': {'OS': update.message.text}})

    reply_keyboard = [['Okay, Bye!']]

    update.message.reply_text(
        '''Thank you! Here is your completion code:

CSH21P4O''',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,resize_keyboard=True
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

    # )
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            CHECK_ID: [MessageHandler(Filters.regex("\w{24}"), train_voice),
                       MessageHandler(Filters.text & (~ Filters.regex("^Withdraw from the study$")), wrongid)],
            INTRO: [MessageHandler(Filters.text & (~ Filters.regex("^Withdraw from the study$")), q1, pass_user_data=True)],
            Q1: [MessageHandler(Filters.regex('^((N|n)ext|(S|s)kip) (Q|q)uestion$'), q1, pass_user_data=True),
                 MessageHandler(Filters.voice & (~ Filters.regex("^Withdraw from the study$")), answer,
                                pass_user_data=True)],
            FINISH: [MessageHandler(Filters.regex("^(Windows|MacOS|Other)$") &
                    (~ Filters.regex("^Withdraw from the study$")), finish1, pass_user_data=True),
                 MessageHandler(Filters.voice & (~ Filters.regex("^Withdraw from the study$")), answer,
                                pass_user_data=True)],
            TRAIN_VOICE: [MessageHandler(Filters.voice, train1)],
            TRAIN1: [MessageHandler(Filters.regex('^(N|n)ext (Q|q)uestion$'), intro_end)],
            INTRO_END: [MessageHandler(Filters.text, q1)]
            #TRAIN2: [MessageHandler(Filters.regex('^Previous Question$'), train3)]
        },
        fallbacks=[MessageHandler(Filters.regex('^Withdraw from the study$'), cancel)],
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
