import re

from telegram import Update
from telegram.ext import (
    CallbackContext,
    Dispatcher,
    Filters,
    MessageHandler,
)


def add_to_bot(dispatcher: Dispatcher):
    pattern = re.compile(r'\bэхо\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    dispatcher.add_handler(
        MessageHandler(msg_filter, echo)
    )


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
