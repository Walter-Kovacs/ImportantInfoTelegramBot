import os
import signal

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters,
)

from components import storage
from components.telegram.filters.update_filters import is_admin
from components.user.interface import UserLoader


def add_to_bot(app: Application):
    app.add_handler(
        CommandHandler('shutdown', shutdown, filters=filters.ChatType.PRIVATE & is_admin)
    )


async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    assert update.effective_chat is not None

    db: UserLoader = storage.get_user_db()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Deactivation accepted.\n\nAll procesess will be stopped.\nOther admins will be notified",
    )

    for admin in db.get_all_admins():
        if admin.tg_id == update.effective_chat.id:
            continue
        await context.bot.send_message(
            chat_id=admin.tg_id,
            text=f"Bot deactivation triggered by admin id: {admin.tg_id}"
        )

    os.kill(os.getpid(), signal.SIGINT)
