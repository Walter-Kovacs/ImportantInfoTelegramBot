import re

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


def add_to_bot(app: Application):
    app.add_handler(CommandHandler('timer', set_timer))

def get_help_info() -> tuple:
    return (
        '/timer 10s[12m, 2h] some_message',
            'Таймер',
            'Поставит персональный таймер на указанное время.\n' +
            'По прошестивю времени тегнет человека в чате ставившего таймер',
            )


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message is None:
        raise AssertionError('effective_message is None in update')

    chat_id = update.effective_message.chat_id
    if context.args is None or len(context.args) == 0:
        command_format = get_help_info()[0]
        await update.effective_message.reply_text(f'Неверный формат команды. Ожидалось что-то такое:\n{command_format}')
        return
    time_str = context.args[0]
    message = ' '.join(context.args[1:])
    await update.effective_message.reply_text(f'parsed timestr: {time_str}\nmessage to remember: {message}')
