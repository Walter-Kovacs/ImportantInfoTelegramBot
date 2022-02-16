from telegram import Update
from telegram.ext.filters import UpdateFilter

import components.storage as storage
from components.user.interface import UserLoader
from components.user.user import User


class IsAdminFilter(UpdateFilter):
    def filter(self, update: Update) -> bool:
        if update.effective_user is None:
            return False

        print(f'IsAdinFilter checks user: {update.effective_user.id}')
        db: UserLoader =  storage.get_user_db()

        user: User = db.load_user_by_telegram_id(update.effective_user.id)
        return user.is_admin


is_admin = IsAdminFilter()
