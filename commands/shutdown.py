import os
import signal
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext

from components.storage import user_db
from components.user.interface import UserLoader

db: UserLoader = user_db


def shutdown(update: Update, context: CallbackContext):
    assert update.effective_chat is not None

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Deactivation accepted.\n\nAll procesess will be stopped.\nOther admins will be notified",
    )

    for admin in db.get_all_admins():
        if admin.tg_id == update.effective_chat.id:
            continue
        context.bot.send_message(chat_id=admin.tg_id, text=f"Bot deactivation triggered by admin id: {admin.tg_id}")

    os.kill(os.getpid(), signal.SIGINT)
