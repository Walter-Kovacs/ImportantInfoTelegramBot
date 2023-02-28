from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
)


def add_to_bot(dispatcher: Dispatcher):
    dispatcher.add_handler(CommandHandler('start', start))


def start(update: Update, context: CallbackContext):
    if update.effective_chat is None:
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, pleas talk to me!")
