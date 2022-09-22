import argparse
import logging

from telegram.ext import Updater
from components.config.config import config
from handlers import add_handlers


def parse_args():
    parser = argparse.ArgumentParser(description='some system args from command line')
    parser.add_argument('--config', type=str, default='config/bot_cfg.json', help='path to bot config json')
    return parser.parse_args()


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    args = parse_args()
    config.read_from_file(args.config)

    token_file = config.data.get('token_path', 'config/token')
    with open(token_file, 'r') as f:
        token = f.readline().strip()

    updater = Updater(token)
    add_handlers(updater.dispatcher)
    updater.start_polling()


if __name__ == '__main__':
    main()
