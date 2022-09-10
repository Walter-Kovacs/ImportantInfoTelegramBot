import logging
import re

from telegram.ext import CommandHandler, Dispatcher, Filters, MessageHandler, CallbackQueryHandler

import bonds
import callbacks
from commands.shutdown import shutdown
from commands.start import start
from components.config import config
from components.telegram.filters.update_filters import is_admin


def add_handlers(dispatcher: Dispatcher):
    logger = logging.getLogger('config.functionality')

    functionality = _get_turned_on_functionality()
    if len(functionality) == 0:
        logger.warning('No functionality configured')
        return

    for elem in functionality:
        functionality_key, re_str = elem

        if functionality_key == 'command_start':
            _add_command_start(dispatcher)
        elif functionality_key == 'command_shutdown':
            _add_command_shutdown(dispatcher)
        elif functionality_key == 'echo':
            _add_echo(dispatcher, re_str)
        elif functionality_key == 'fact':
            _add_fact(dispatcher, re_str)
        elif functionality_key == 'bonds':
            _add_bonds(dispatcher, re_str)
        elif functionality_key == 'game_mock':
            _add_game_mock(dispatcher, re_str)
        else:
            continue

        logger.info(f'Turn on functionality: {functionality_key}')


def _get_turned_on_functionality() -> list:
    """
    Return a list of tuples (functionality key, re string) from functionality config file sorted by priority.
    Functionality config file should consist of such lines:
    <functionality key>:<priority of adding handler>:[optional regular expression for message the bot replay to]
    """
    functionality = list()

    functionality_file_path = config.config.data.get('functionality', None)
    if functionality_file_path is not None:
        with open(functionality_file_path, 'r') as file:
            line = file.readline()
            while line != '':
                _parse_functionality_file_line(functionality, line)
                line = file.readline()

    functionality.sort(key=lambda el: el[0])
    for i in range(len(functionality)):
        functionality[i] = (functionality[i][1], functionality[i][2])
    return functionality


def _parse_functionality_file_line(functionality: list, line: str):
    logger = logging.getLogger('config.functionality')

    split = line.strip().split(':', 2)
    if len(split) < 2:
        logger.warning(f'Skipping functionality config-file line: {line.strip()}')
        return
    if not split[1].isdigit():
        logger.warning(f'Skipping functionality config-file line: {line.strip()}')
        return

    if len(split) == 2:
        split.append('')

    key, priority, re_str = split
    functionality.append((int(priority), key, re_str))


def _add_command_start(dispatcher: Dispatcher):
    handler = CommandHandler('start', start)
    dispatcher.add_handler(handler)


def _add_command_shutdown(dispatcher: Dispatcher):
    handler = CommandHandler('shutdown', shutdown, filters=Filters.chat_type.private & is_admin)
    dispatcher.add_handler(handler)


def _add_echo(dispatcher: Dispatcher, re_str: str):
    if re_str != '':
        echo_re = re.compile(re_str, re.IGNORECASE)
    else:
        echo_re = re.compile(r'\bэхо\b', re.IGNORECASE)

    msg_filter = Filters.text & (~Filters.command) & Filters.regex(echo_re)
    handler = MessageHandler(msg_filter, callbacks.echo_callback)
    dispatcher.add_handler(handler)


def _add_fact(dispatcher: Dispatcher, re_str: str):
    if re_str != '':
        fact_ask_re = re.compile(re_str, re.IGNORECASE)
    else:
        fact_ask_re = re.compile(r'^(расскажи|давай|дай-ка|хочу)\s+факт', re.IGNORECASE)

    msg_filter = Filters.text & (~Filters.command) & Filters.regex(fact_ask_re)
    update_filter = Filters.chat_type.private | Filters.chat_type.group | Filters.chat_type.supergroup
    handler = MessageHandler(msg_filter & update_filter, callbacks.random_important_fact_callback)
    dispatcher.add_handler(handler)


def _add_bonds(dispatcher: Dispatcher, re_str: str):
    if re_str != '':
        kb_re = re.compile(re_str, re.IGNORECASE)
    else:
        kb_re = re.compile(r'\bbonds\b', re.IGNORECASE)

    msg_filter = Filters.text & (~Filters.command) & Filters.regex(kb_re)
    handler = MessageHandler(msg_filter, bonds.start_callback)
    dispatcher.add_handler(handler)
    dispatcher.add_handler(CallbackQueryHandler(bonds.keyboard_callback, pattern=r'^bonds'))


def _add_game_mock(dispatcher: Dispatcher, re_str: str):
    if re_str != '':
        game_request_re = re.compile(re_str, re.IGNORECASE)
    else:
        game_request_re = re.compile(r'\bпартеечку\b', re.IGNORECASE)

    msg_filter = Filters.text & (~Filters.command) & Filters.regex(game_request_re)
    handler = MessageHandler(msg_filter, callbacks.game_request_callback)
    dispatcher.add_handler(handler)
