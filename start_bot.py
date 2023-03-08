import argparse
import importlib
import logging
import os
from pathlib import Path
from typing import List, Tuple

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Updater,
)

from components.config.config import config

functionalities_help: str


def parse_args():
    parser = argparse.ArgumentParser(description='some system args from command line')
    parser.add_argument('--config', type=str, default='config/bot_cfg.json', help='path to bot config json')
    return parser.parse_args()


def load_functionalities(dispatcher: Dispatcher):
    functionalities_directory = 'functionalities'
    paths = [
        path for path in
        [Path(functionalities_directory) / el for el in os.listdir(functionalities_directory)]
        if path.is_dir() and path.name != '__pycache__'
    ]

    f_help = []
    for path in paths:
        functionality = importlib.import_module(f'{functionalities_directory}.{path.name}')
        functionality.add_to_bot(dispatcher)

        try:
            help_functionality_name, help_functionality_description = functionality.get_help_info()
            f_help.append((help_functionality_name, help_functionality_description))
        except AttributeError:
            pass

    f_help.sort()
    construct_functionalities_help_string(f_help)


def construct_functionalities_help_string(f_help: List[Tuple[str, str]]):
    res = ['Функциональности бота:\n']
    for title, description in f_help:
        res.append(f'{title}\n{description}\n')

    global functionalities_help
    functionalities_help = '\n'.join(res)


def functionalities_help_callback(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=functionalities_help)


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    args = parse_args()
    config.read_from_file(args.config)

    token_file = config.data.get('token_path', 'config/token')
    with open(token_file, 'r') as f:
        token = f.readline().strip()

    updater = Updater(token)
    load_functionalities(updater.dispatcher)
    updater.dispatcher.add_handler(CommandHandler('help', functionalities_help_callback))
    updater.start_polling()


if __name__ == '__main__':
    main()
