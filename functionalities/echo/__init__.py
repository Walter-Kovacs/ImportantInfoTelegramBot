import re

from telegram import Update
from telegram.ext import (
    Filters,
    MessageHandler, CallbackContext,
)


def add_to_bot(updater):
    pattern = re.compile(r'\bэхо\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    updater.dispatcher.add_handler(
        MessageHandler(msg_filter, echo)
    )


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
