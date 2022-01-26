import logging
import re

from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from commands.start import start
from msg import parse_message
from msg.random_fact import get_random_important_fact

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

with open('config/token', 'r') as f:
    TOKEN = f.readline().strip()

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), parse_message)
fact_ask_re = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)
random_important_fact_msg_filter = Filters.text & (~Filters.command) & Filters.regex(fact_ask_re)

random_important_fact_handler = MessageHandler(random_important_fact_msg_filter, get_random_important_fact)


# order is important
dispatcher.add_handler(random_important_fact_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()
