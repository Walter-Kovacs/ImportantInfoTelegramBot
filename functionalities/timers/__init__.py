import logging
import re
import traceback
import datetime
from typing import Dict, List, Optional, Tuple
from attrs import define

from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, CommandHandler, ContextTypes, Job

logger = logging.getLogger(__name__)

def add_to_bot(app: Application):
    app.add_handler(CommandHandler('timer', set_timer))

job_queue_pref = __name__
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
            'Таймер\n' +
            'Без аргументов: покажет поставленные вами тамймеры.\n\n' +
            'С аргументами: Поставит персональный таймер на указанное время.\n' +
            'По прошестивю времени тегнет человека в чате ставившего таймер\n' +
            f'Время поддерживается в формате: [{" ".join(time_symbols_for_help)}]',
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

@define
class TimerCallbackData:
    message: str

async def timer_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    job = context.job
    if job is None:
        logger.error('job is None in CallbackContext')
        return
    chat_id = job.chat_id
    if chat_id is None:
        logger.error('job from CallbackContext has no chat_id')
        return
    user_data = context.user_data
    if user_data is None:
        logger.error('user_data is None callback context')
        return
    username = user_data.get('username', '')
    if username == '':
        logger.error('username is missed in user_data')
        return

    user_tag_prefix = f'@{username}, '
    if context.chat_data is not None and context.chat_data.get('chat_type', '') == ChatType.PRIVATE:
        # don't tag in private chat
        user_tag_prefix = ''

    # validation, that sends msg to telegram if errors occured
    data = job.data
    if data is None or not isinstance(data, TimerCallbackData):
        await context.bot.send_message(chat_id, text=f'{user_tag_prefix}таймер истёк, но о чём он должен был напомнить я потерял :(')
        return

    if data.message == '':
        await context.bot.send_message(chat_id, text=f'{user_tag_prefix} таймер истёк. Он был без описания')
        return

    await context.bot.send_message(chat_id, text=f"{user_tag_prefix} таймер истёк. Он был про '{data.message}' (c)")

def format_timer_jobs(jobs: Tuple[Job, ... ]) -> str:
    if len(jobs) == 0:
        return 'Нет активных таймеров'
    active_timers: List[str] = []
    for j in jobs:
        dt = j.job.next_run_time - datetime.datetime.now(tz=j.job.next_run_time.tzinfo)
        dt = str(dt).split('.')[0] # remove miliseconds from string format
        timer_msg = 'Таймер без описания'
        job_data = j.data
        if job_data is not None and isinstance(job_data, TimerCallbackData):
            if job_data.message != '':
                timer_msg = job_data.message
        else:
            logger.error(f'format_timer_jobs: job: {j.name} has unexpected job.data: {job_data}; should be TimerCallbackData obj')
        active_timers.append( 'через {} - {}'.format(dt, timer_msg))

    return 'Активные таймеры:\n' + '\n'.join(active_timers)



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

    queue_key = f'{job_queue_pref}_{user.id}'
    timers_for_this_user = job_queue.get_jobs_by_name(queue_key)
    if context.args is None or len(context.args) == 0:
        await update.effective_message.reply_text(format_timer_jobs(timers_for_this_user))
        return

    timer_seconds, timer_message, error_msg = validate_args(context.args)
    if error_msg is not None:
        await update.effective_message.reply_text(error_msg)
        return

    if timers_for_this_user is not None and len(timers_for_this_user) >= max_timer_per_user:
        await update.effective_message.reply_text('Слишком много таймеров для одного, новый не поставлю.')
        return

    # fill user and chat data in context
    if context.user_data is None:
        context.user_data = {
            'username': user.username,
        }
    else:
        context.user_data['username'] = user.username

    if context.chat_data is None:
        context.chat_data = {
            'chat_type': update.effective_message.chat.type,
        }
    else:
        context.chat_data['chat_type'] = update.effective_message.chat.type

    job_queue.run_once(
        timer_callback, timer_seconds,
        name=queue_key,
        user_id=user.id,
        chat_id=chat_id,
        data=TimerCallbackData(
            message=timer_message,
        ),
    )
    await update.effective_message.reply_text(f'Таймер поставлен')
