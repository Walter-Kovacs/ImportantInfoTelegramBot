import logging
import re

from telegram.ext import (CommandHandler, Dispatcher, Filters, MessageHandler,
                          Updater)

import callbacks
from commands.shutdown import shutdown
from commands.start import start
from components.telegram.filters.update_filters import is_admin


def add_handlers(dispatcher: Dispatcher):
    handler = CommandHandler('start', start)
    dispatcher.add_handler(handler)

    handler = CommandHandler('shutdown', shutdown, filters=Filters.chat_type.private & is_admin)
    dispatcher.add_handler(handler)

    fact_ask_re = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(fact_ask_re)
    handler = MessageHandler(msg_filter, callbacks.random_important_fact_callback)

    game_request_re = re.compile(r'\bпартеечку\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(game_request_re)
    update_filter = Filters.chat_type.private | Filters.chat_type.group
    handler = MessageHandler(update_filter & msg_filter, callbacks.game_request_callback)
    dispatcher.add_handler(handler)

    echo_re = re.compile(r'\bэхо\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(echo_re)
    handler = MessageHandler(msg_filter, callbacks.echo_callback)
    dispatcher.add_handler(handler)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('config/token', 'r') as f:
        token = f.readline().strip()

    updater = Updater(token)
    add_handlers(updater.dispatcher)
    updater.start_polling()


if __name__ == '__main__':
    main()
