from telegram import Update
from telegram.ext import CallbackContext

from .echo import echo
from .game_call import simple_answer


def parse_message(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg.find("эхо") != -1:
        echo(update, context)
    if msg.find("партеечку") != -1:
        simple_answer(update, context)
