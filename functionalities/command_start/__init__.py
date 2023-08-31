from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)


def add_to_bot(app: Application):
    app.add_handler(CommandHandler('start', start))


def get_help_info() -> tuple:
    return '/start', 'Приветствие от бота.'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat is None:
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, pleas talk to me! Or type /help")
