from telegram import Update
from telegram.ext import CallbackContext


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
