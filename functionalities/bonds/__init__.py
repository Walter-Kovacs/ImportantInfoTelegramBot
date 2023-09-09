import re

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from .callbacks import start_callback, keyboard_callback


def add_to_bot(app: Application):
    pattern = re.compile(r'\bbonds\b', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    handler = MessageHandler(msg_filter, start_callback)
    app.add_handler(handler)
    app.add_handler(CallbackQueryHandler(keyboard_callback, pattern=r'^bonds'))


def get_help_info() -> tuple:
    return (
        'Расчёт доходности облигации.',
        'Запускается, если в сообщении есть слово bonds.'
    )
