import logging
import re
from typing import Dict, List, Optional, Tuple

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

def add_to_bot(app: Application):
    app.add_handler(CommandHandler('timer', set_timer))

max_timer_seconds = 3600 * 24 # Allow to set timer up to one day only
max_timer_per_user = 5

# Order important for help string
time_symbols_to_seconds = [
    ('s', 1),
    ('m', 60),
    ('h', 3600),
    ('с', 1),
    ('м', 60),
    ('ч', 3600),
]

# Dict for convenient usage in code below
time_symbols_dict: Dict[str, int] = { tpl[0]: tpl[1] for tpl in time_symbols_to_seconds }

# List of time symbols in suitable for help string order
time_symbols: List[str] = [tpl[0] for tpl in time_symbols_to_seconds]

time_symbols_for_help = [f'N{elem}' for elem in time_symbols]

time_str_re = re.compile(r'^(\d+)('+'|'.join(time_symbols) +')$')

def get_help_info() -> tuple:
    return (
        '/timer 10s[12m, 2h] some_message',
            'Таймер',
            'Поставит персональный таймер на указанное время.\n' +
            'По прошестивю времени тегнет человека в чате ставившего таймер\n' +
            f'Время поддерживается в формате: {time_symbols_for_help}',
            )

def validate_args(args: Optional[List[str]]) -> Tuple[int, str, Optional[str]]:
    if args is None or len(args) == 0:
        command_format = get_help_info()[0]
        return (0, '', f'Неверный формат команды. Ожидалось что-то такое:\n{command_format}')

    time_str = args[0]
    message = ' '.join(args[1:])
    matched = time_str_re.match(time_str)
    if matched is None:
        return (0, '',
            f'Неверный формат команды. Передано неправильное время: {time_str}\n'+
            f'Поддерживаемые форматы {time_symbols_for_help}',
        )
    (amount_str, modificator) = matched.groups()
    try:
        seconds = time_symbols_dict[modificator]
    except KeyError as e:
        logger.error(f'Time modificator "{modificator}" definition not found in time_symbols_dict {time_symbols_dict}')
        return (0, '', 'Что-то пошло не так')

    timer_seconds = int(amount_str) * seconds
    if timer_seconds > max_timer_seconds:
        return (0, '', 'Не могу поставить таймер более чем на сутки')

    # regexp time_str_re blocks negative numbers. but there better to have this additional check than don't have
    if timer_seconds <= 0:
        return (0, '', 'Отрицательное или нулевое время? Хорошая попытка')

    return timer_seconds, message, None

async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_message is None:
        raise AssertionError('effective_message is None in update')

    job_queue = context.job_queue
    if job_queue is None:
        logger.error('job_queue is None, timers functionality is not available')
        await update.effective_message.reply_text('К сожалению, таймеры пока недоступны')
        return

    chat_id = update.effective_message.chat_id
    user = update.effective_message.from_user
    if user is None:
        logger.error('from_user is None in effective_chat')
        await update.effective_message.reply_text(f'Что-то пошло не так')
        return

    timer_seconds, timer_message, error_msg = validate_args(context.args)
    if error_msg is not None:
        await update.effective_message.reply_text(error_msg)
        return

    timers_for_this_user = job_queue.get_jobs_by_name(f'{user.id}')
    if timers_for_this_user is not None and len(timers_for_this_user) > max_timer_per_user:
        await update.effective_message.reply_text('Слишком много таймеров для одного, новый не поставлю.')
        return

    await update.effective_message.reply_text(f'chat: {chat_id}, user: {user}')
