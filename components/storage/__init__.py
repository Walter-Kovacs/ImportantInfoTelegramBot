from components.config.config import config

from .dict_db import DictDB


class StorageException(Exception):
    pass


user_db = None


def get_user_db() -> DictDB:
    global user_db
    if user_db is not None:
        return user_db

    json_user_db_filepath = config.data.get('storage', {}).get('json_user_db_filepath', '')

    if not json_user_db_filepath:
        raise StorageException('there is no json_user_db file path in config')

    user_db = DictDB()
    user_db.load_from_file(json_user_db_filepath)
    return user_db
