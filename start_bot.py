import argparse
import importlib
import logging
import os
import traceback
from pathlib import Path
from typing import List, Tuple

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
)

from components.config.config import config

functionalities_help: str


def parse_args():
    parser = argparse.ArgumentParser(description='some system args from command line')
    parser.add_argument('--config', type=str, default='config/bot_cfg.json', help='path to bot config json')
    return parser.parse_args()


def load_functionalities(app: Application):
    functionalities_directory = 'functionalities'
    paths = [
        path for path in
        [Path(functionalities_directory) / el for el in os.listdir(functionalities_directory)]
        if path.is_dir() and path.name != '__pycache__'
    ]

    f_help = []
    enable_or_disable, functionalities_in_config = get_enable_disable_functionalities_list()
    for path in paths:
        if enable_or_disable == 'enable':
            if path.name not in functionalities_in_config:
                continue
            logging.info(f'Functionality {path.name} enabled')
        if enable_or_disable == 'disable':
            if path.name in functionalities_in_config:
                logging.info(f'Functionality {path.name} disabled')
                continue

        try:
            functionality = importlib.import_module(f'{functionalities_directory}.{path.name}')
            functionality.add_to_bot(app)
        except Exception:
            logging.warning(f'Cannot load functionality: {path}\n{traceback.format_exc()}')
            continue

        try:
            help_functionality_name, help_functionality_description = functionality.get_help_info()
            f_help.append((help_functionality_name, help_functionality_description))
        except AttributeError:
            pass
        except ValueError:
            logging.warning(f'Cannot create helpstring for functionality: {path}\n{traceback.format_exc()}')

    f_help.sort()
    construct_functionalities_help_string(f_help)


def get_enable_disable_functionalities_list() -> Tuple[str, List[str]]:
    """
    Config file:
{
  ...
  "functionalities": {
    "enable": [],
    "disable": []
  }
  ...
}
    Returns:
        ('enable' or 'disable', ['functionality, ...'])
    """
    f: dict = config.data.get('functionalities', dict())
    if 'enable' in f:
        return 'enable', f.get('enable')
    return 'disable', f.get('disable', list())


def construct_functionalities_help_string(f_help: List[Tuple[str, str]]):
    res = ['Функциональности бота:\n']
    for title, description in f_help:
        res.append(f'{title}\n{description}\n')

    global functionalities_help
    functionalities_help = '\n'.join(res)


async def functionalities_help_callback(update: Update, context: CallbackContext):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=functionalities_help)


def main():
    loggingFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=loggingFormat, level=logging.INFO)

    args = parse_args()
    config.read_from_file(args.config)
    logging_level_from_conf = config.data.get('logging', {}).get('level', '')
    if logging_level_from_conf != "":
        level = logging.getLevelName(logging_level_from_conf)
        assert isinstance(level, int), f"unsupported level name red from bot conf: '{logging_level_from_conf}'"
        logging.basicConfig(format=loggingFormat, level=level, force=True)
        logging.info(f"Logging level set to config's value to {logging_level_from_conf} ({level})")
    else:
        logging.info('Logging level not found in bot config (logging.level json 2nd level key), continue with level INFO')

    token_file = config.data.get('token_path', 'config/token')
    with open(token_file, 'r') as f:
        token = f.readline().strip()

    app = ApplicationBuilder().token(token).build()
    load_functionalities(app)
    app.add_handler(CommandHandler('help', functionalities_help_callback))
    app.run_polling()


if __name__ == '__main__':
    main()
