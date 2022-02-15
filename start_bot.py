import logging
import re

from telegram.ext import CallbackQueryHandler, CommandHandler, Dispatcher, Filters, MessageHandler, Updater

import bonds
import callbacks
from commands.start import start


def add_handlers(dispatcher: Dispatcher):
    handler = CommandHandler('start', start)
    dispatcher.add_handler(handler)

    fact_ask_re = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(fact_ask_re)
    handler = MessageHandler(msg_filter, callbacks.random_important_fact_callback)
    dispatcher.add_handler(handler)

    game_request_re = re.compile(r'\bпартеечку\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(game_request_re)
    handler = MessageHandler(msg_filter, callbacks.game_request_callback)
    dispatcher.add_handler(handler)

    echo_re = re.compile(r'\bэхо\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(echo_re)
    handler = MessageHandler(msg_filter, callbacks.echo_callback)
    dispatcher.add_handler(handler)

    kb_re = re.compile(r'\bbonds\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(kb_re)
    handler = MessageHandler(msg_filter, bonds.bonds_request_callback)
    dispatcher.add_handler(handler)
    dispatcher.add_handler(CallbackQueryHandler(bonds.keyboard_callback))


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    with open('config/token', 'r') as f:
        token = f.readline().strip()

    updater = Updater(token)
    add_handlers(updater.dispatcher)
    updater.start_polling()


if __name__ == '__main__':
    main()
