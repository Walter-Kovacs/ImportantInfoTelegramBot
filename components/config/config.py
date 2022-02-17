import json
from typing import Dict


class Config:
    data: Dict = {}

    def read_from_file(cls, config_path: str) -> None:
        with open(config_path, 'r') as config_file:
            cls.data = json.load(config_file)

        print('Config loaded successfull')


config = Config()
