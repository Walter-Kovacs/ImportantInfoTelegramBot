import logging
import re
import time

from telegram import Update
from telegram.ext import CallbackContext, Dispatcher, Filters, MessageHandler

_logger = logging.getLogger(__name__)

def add_to_bot(dispatcher: Dispatcher):
    pattern = re.compile(r'\b(партеечку|когда соберёмся?)\b', re.IGNORECASE)
    msg_filter = Filters.text & (~Filters.command) & Filters.regex(pattern)
    handler = MessageHandler(msg_filter, game_request_callback)
    dispatcher.add_handler(handler)


def game_request_callback(update: Update, context: CallbackContext):
    assert update.effective_chat, "effective_chat not found in update obj"
    assert update.message, "message not found in update obj"
    # start poll
    chat_id=update.effective_chat.id
    context.bot.send_message(chat_id=chat_id, text="Ну поехали искать день...")
    time.sleep(1)
    sent_message = context.bot.send_poll(chat_id=chat_id,
        question="Есть ли у вас время в ближайший месяц, чтобы сходить на 2-3 часика в Don't Starve Together",
                          options=['Да', 'Нет', 'Смогу выделить, если наберётся критическая масса'],
                          is_anonymous=False,
                          )
    _logger.debug(f'message with poll: {sent_message}')


