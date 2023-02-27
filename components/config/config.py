import json
import logging
from typing import Dict


class Config:
    data: Dict = {}

    @classmethod
    def read_from_file(cls, config_path: str) -> None:
        with open(config_path, 'r') as config_file:
            cls.data = json.load(config_file)

        logger = logging.getLogger('config')
        logger.info('Config loaded successfully')


config = Config()
