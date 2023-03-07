from telegram.ext import (
    CommandHandler,
    Dispatcher,
)

from functionalities.currencies.callbacks import (
    currency_command_callback,
)


def add_to_bot(dispatcher: Dispatcher):
    dispatcher.add_handler(CommandHandler('currency', currency_command_callback))


def get_help_info() -> tuple:
    return (
        'Курс валюты.',
        'Команда: "/currency [code] [date]" отображает курс валюты на указанную дату.'
    )
