import re

from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)


def add_to_bot(app: Application):
    pattern = re.compile(r'\bпартеечку\b', re.IGNORECASE)
    msg_filter = filters.TEXT & (~filters.COMMAND) & filters.Regex(pattern)
    handler = MessageHandler(msg_filter, game_request_callback)
    app.add_handler(handler)


async def game_request_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=decline_game_request(update.message.text))


def decline_game_request(msg: str) -> str:
    msg_lower = msg.lower()
    if msg_lower.find("цивилизацию") != -1 or msg_lower.find("циву") != -1:
        return "Цивилизация - это не модно. Вот Don't Starve - другое дело!"
    else:
        return "Похоже, что сейчас никто не готов играть :("
