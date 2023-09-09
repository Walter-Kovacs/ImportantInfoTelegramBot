import re

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

from .random_fact import get_random_important_fact


def add_to_bot(app: Application):
    pattern = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    update_filter = filters.ChatType.PRIVATE | filters.ChatType.GROUP | filters.ChatType.SUPERGROUP
    handler = MessageHandler(msg_filter & update_filter, random_important_fact_callback)
    app.add_handler(handler)


def get_help_info() -> tuple:
    return (
        'Факты.',
        'Присылает случайный (очень важный) факт на сообщения "расскажи/давай/дай-ка/хочу факт".'
    )


async def random_important_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'preparing random fact')

    chat_type = update.effective_chat.type
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_random_important_fact(),
        parse_mode=ParseMode.HTML,
        reply_to_message_id=update.message.message_id if chat_type in ['group', 'supergroup'] else None,
    )
