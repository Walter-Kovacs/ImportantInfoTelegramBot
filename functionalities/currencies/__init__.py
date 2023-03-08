from telegram.ext import (
    CommandHandler,
    Dispatcher,
)

from functionalities.currencies.callback import (
    show_main_currencies,
)


def add_to_bot(dispatcher: Dispatcher):
    dispatcher.add_handler(CommandHandler('currency', show_main_currencies))


def get_help_info() -> tuple:
    return '/currency', 'Курс основных валют за текущую дату.'
