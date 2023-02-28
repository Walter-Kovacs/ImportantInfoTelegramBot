from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from msg import simple
from msg.random_fact import get_random_important_fact


def game_request_callback(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=simple.decline_game_request(update.message.text))


def random_important_fact_callback(update: Update, context: CallbackContext):
    print(f'preparing random fact')

    chat_type =update.effective_chat.type
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_random_important_fact(),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id if chat_type in ['group','supergroup'] else None,
    )
