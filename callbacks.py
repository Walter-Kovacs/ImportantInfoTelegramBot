from telegram import Update
from telegram.ext import CallbackContext

from msg import simple
from msg.random_fact import get_random_important_fact


def echo_callback(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=simple.echo(update.message.text)
    )


def game_request_callback(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=simple.decline_game_request(update.message.text)
    )


def random_important_fact_callback(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_random_important_fact()
    )