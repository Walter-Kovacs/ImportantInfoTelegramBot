import re

from telegram.ext import (
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
)

from . import callbacks


def add_to_bot(dispatcher: Dispatcher):
    # Command /currency
    dispatcher.add_handler(CommandHandler('currency', callbacks.currency_command_callback))
    dispatcher.add_handler(CommandHandler('currency_available', callbacks.currency_available_command_callback))

    # Message "курс биткоина" - BTC rate for today
    pattern = re.compile(r'\bкурс\b +\bбитко[и,й]на\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    dispatcher.add_handler(MessageHandler(msg_filter, callbacks.bitcoin_rate_callback))

    # Message "курс <currency>" - currency rate for today
    pattern = re.compile(r'^курс +[а-я]+', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    dispatcher.add_handler(MessageHandler(msg_filter, callbacks.start_with_keyword_callback))


def get_help_info() -> tuple:
    return (
        'Курс валюты.',
        'Команда: "/currency [code] [date]" отображает курс валюты на указанную дату.\n'
        'Команда: "/currency_available" отображает достуные валюты.\n'
        'На сообщения вида "курс <название валюты>" присылает курс указанной валюты на сегодня.'
    )
