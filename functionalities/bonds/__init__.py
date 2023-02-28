import re

from telegram.ext import (
    CallbackQueryHandler,
    Dispatcher,
    Filters,
    MessageHandler,
)

from .callbacks import start_callback, keyboard_callback


def add_to_bot(dispatcher: Dispatcher):
    pattern = re.compile(r'\bbonds\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    handler = MessageHandler(msg_filter, start_callback)
    dispatcher.add_handler(handler)
    dispatcher.add_handler(CallbackQueryHandler(keyboard_callback, pattern=r'^bonds'))
