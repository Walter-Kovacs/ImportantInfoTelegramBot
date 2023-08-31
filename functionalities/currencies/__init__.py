import re

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from . import callbacks


def add_to_bot(app: Application):
    # Command /currency
    app.add_handler(CommandHandler('currency', callbacks.currency_command_callback))
    app.add_handler(CommandHandler('currency_available', callbacks.currency_available_command_callback))

    # Message "курс биткоина" - BTC rate for today
    pattern = re.compile(r'\bкурс\b +\bбитко[и,й]на\b', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    app.add_handler(MessageHandler(msg_filter, callbacks.bitcoin_rate_callback))

    # Message "курс <currency>" - currency rate for today
    pattern = re.compile(r'^курс +[а-я]+', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    app.add_handler(MessageHandler(msg_filter, callbacks.start_with_keyword_callback))


def get_help_info() -> tuple:
    return (
        'Курс валюты.',
        'Команда: "/currency [code] [date]" отображает курс валюты на указанную дату.\n'
        'Команда: "/currency_available" отображает достуные валюты.\n'
        'На сообщения вида "курс <название валюты>" присылает курс указанной валюты на сегодня.'
    )
