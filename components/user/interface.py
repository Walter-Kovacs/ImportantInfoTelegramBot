from typing import List, Protocol

from .user import User


class UserLoader(Protocol):
    @classmethod
    def load_user_by_telegram_id(cls, tg_id: int) -> User:
        pass

    @classmethod
    def get_all_admins(cls) -> List[User]:
        pass
