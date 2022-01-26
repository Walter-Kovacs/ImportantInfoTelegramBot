from telegram import Update
from telegram.ext import CallbackContext


def echo(update: Update, context: CallbackContext):
    if update.effective_chat is not None and update.message is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
