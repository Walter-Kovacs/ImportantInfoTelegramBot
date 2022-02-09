from telegram import Update
from telegram.ext.filters import UpdateFilter

from components.storage import user_db
from components.user.interface import UserLoader
from components.user.user import User

db: UserLoader = user_db


class IsAdminFilter(UpdateFilter):
    def filter(self, update: Update) -> bool:
        if update.effective_user is None:
            return False

        print(f'IsAdinFilter checks user: {update.effective_user.id}')
        user: User = db.load_user_by_telegram_id(update.effective_user.id)
        return user.is_admin


is_admin = IsAdminFilter()
