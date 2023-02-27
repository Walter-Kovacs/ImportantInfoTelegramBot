import argparse
import importlib
import logging
import os
from pathlib import Path

from telegram.ext import Updater
from components.config.config import config


def parse_args():
    parser = argparse.ArgumentParser(description='some system args from command line')
    parser.add_argument('--config', type=str, default='config/bot_cfg.json', help='path to bot config json')
    return parser.parse_args()


def load_functionalities(updater):
    functionalities_directory = 'functionalities'
    paths = [
        path for path in
        [Path(functionalities_directory) / el for el in os.listdir(functionalities_directory)]
        if path.is_dir() and path.name != '__pycache__'
    ]
    for path in paths:
        functionality = importlib.import_module(f'{functionalities_directory}.{path.name}')
        functionality.add_to_bot(updater)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    args = parse_args()
    config.read_from_file(args.config)

    token_file = config.data.get('token_path', 'config/token')
    with open(token_file, 'r') as f:
        token = f.readline().strip()

    updater = Updater(token)
    load_functionalities(updater)
    updater.start_polling()


if __name__ == '__main__':
    main()
