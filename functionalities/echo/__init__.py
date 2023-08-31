import re

from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
    ContextTypes,
    MessageHandler,
    filters,
)


def add_to_bot(app: Application):
    pattern = re.compile(r'\bэхо\b', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    app.add_handler(
        MessageHandler(msg_filter, echo)
    )


def get_help_info() -> tuple:
    return (
        'Эхо.',
        'Ответ на сообщения со словом эхо.'
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
