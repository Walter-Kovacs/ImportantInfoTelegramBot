import json
from typing import Dict, List

from components.user.user import User


class DictDB:
    _user_data: Dict[int, dict] = {}

    @classmethod
    def load_from_file(cls, filename: str) -> None:
        with open(filename, 'r') as f:
            json_data = json.load(f)
            cls._user_data = {int(tg_id): user_data for tg_id, user_data in json_data.items()}

        print(f'users_db loaded from file sucessfully')

    @classmethod
    def load_user_by_telegram_id(cls, tg_user_id: int) -> User:
        user_data = cls._user_data.get(tg_user_id, {})

        return User(tg_id=tg_user_id, is_admin=user_data.get('admin', False))

    @classmethod
    def get_all_admins(cls) -> List[User]:
        return [User(tg_id, is_admin=True) for tg_id, user in cls._user_data.items() if user.get('admin', False)]
