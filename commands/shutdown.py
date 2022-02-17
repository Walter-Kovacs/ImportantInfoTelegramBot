import os
import signal
from typing import Optional

from telegram import Update
from telegram.ext import CallbackContext

import components.storage as storage
from components.user.interface import UserLoader


def shutdown(update: Update, context: CallbackContext):
    assert update.effective_chat is not None

    db: UserLoader = storage.get_user_db()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Deactivation accepted.\n\nAll procesess will be stopped.\nOther admins will be notified",
    )

    for admin in db.get_all_admins():
        if admin.tg_id == update.effective_chat.id:
            continue
        context.bot.send_message(chat_id=admin.tg_id, text=f"Bot deactivation triggered by admin id: {admin.tg_id}")

    os.kill(os.getpid(), signal.SIGINT)
