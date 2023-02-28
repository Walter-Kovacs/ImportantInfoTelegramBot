import re

from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    Dispatcher,
    Filters,
    MessageHandler,
)

from .random_fact import get_random_important_fact


def add_to_bot(dispatcher: Dispatcher):
    pattern = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    update_filter = Filters.chat_type.private | Filters.chat_type.group | Filters.chat_type.supergroup
    handler = MessageHandler(msg_filter & update_filter, random_important_fact_callback)
    dispatcher.add_handler(handler)


def random_important_fact_callback(update: Update, context: CallbackContext):
    print(f'preparing random fact')

    chat_type = update.effective_chat.type
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_random_important_fact(),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id if chat_type in ['group', 'supergroup'] else None,
    )
