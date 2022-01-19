import logging
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from commands.start import start
from msg import parse_message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

with open('config/token', 'r') as f:
    TOKEN = f.readline()

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), parse_message)
dispatcher.add_handler(echo_handler)

updater.start_polling()
