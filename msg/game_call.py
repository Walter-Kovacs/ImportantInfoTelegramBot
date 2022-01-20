from telegram import Update
from telegram.ext import CallbackContext


def simple_answer(update: Update, context: CallbackContext):
    if update.effective_chat is not None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Похоже, что сейчас никто не готов")
