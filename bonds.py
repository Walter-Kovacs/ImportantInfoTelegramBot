from datetime import datetime
from enum import Enum
from typing import List

from components.bonds import get_yield_to_maturity
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


class InputStep(Enum):
    FACE_VALUE = 1,
    COUPON_RATE = 2,
    MATURITY_DATE = 3,
    MARKET_PRICE = 4,
    END = 5


class UnknownInputStep(Exception):
    pass


class StepParam(Enum):
    NEXT_STEP = 1,
    MSG_HEADER = 2,
    EDITING_PARAM_TITLE = 3


_STEP_PARAMS = {
    InputStep.FACE_VALUE: {
        StepParam.NEXT_STEP: InputStep.COUPON_RATE,
        StepParam.MSG_HEADER: 'Введите номинал облигации',
        StepParam.EDITING_PARAM_TITLE: 'Номинал'
    },
    InputStep.COUPON_RATE: {
        StepParam.NEXT_STEP: InputStep.MATURITY_DATE,
        StepParam.MSG_HEADER: 'Введите купон в процентах',
        StepParam.EDITING_PARAM_TITLE: 'Купон (%)'
    },
    InputStep.MATURITY_DATE: {
        StepParam.NEXT_STEP: InputStep.MARKET_PRICE,
        StepParam.MSG_HEADER: 'Введите дату погашения в формате дд.мм.гггг',
        StepParam.EDITING_PARAM_TITLE: 'Дата погашения'
    },
    InputStep.MARKET_PRICE: {
        StepParam.NEXT_STEP: InputStep.END,
        StepParam.MSG_HEADER: 'Введите рыночную цену',
        StepParam.EDITING_PARAM_TITLE: 'Цена'
    }
}


def _get_next_step(step: InputStep) -> InputStep:
    if step in _STEP_PARAMS:
        return _STEP_PARAMS[step][StepParam.NEXT_STEP]

    raise UnknownInputStep('Unknown input step')


def _get_msg_header(step: InputStep) -> str:
    if step in _STEP_PARAMS:
        return _STEP_PARAMS[step][StepParam.MSG_HEADER]

    raise UnknownInputStep('Unknown input step')


def _get_step_by_msg_header(header: str) -> InputStep:
    for step in _STEP_PARAMS:
        if _STEP_PARAMS[step][StepParam.MSG_HEADER] == header:
            return step

    raise UnknownInputStep('Unknown step message header')


def _get_editing_param_title(step: InputStep) -> str:
    if step in _STEP_PARAMS:
        return _STEP_PARAMS[step][StepParam.EDITING_PARAM_TITLE]

    raise UnknownInputStep('Unknown input step')


def get_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('7', callback_data='7'),
                InlineKeyboardButton('8', callback_data='8'),
                InlineKeyboardButton('9', callback_data='9'),
            ],
            [
                InlineKeyboardButton('4', callback_data='4'),
                InlineKeyboardButton('5', callback_data='5'),
                InlineKeyboardButton('6', callback_data='6'),
            ],
            [
                InlineKeyboardButton('1', callback_data='1'),
                InlineKeyboardButton('2', callback_data='2'),
                InlineKeyboardButton('3', callback_data='3'),
            ],
            [
                InlineKeyboardButton('0', callback_data='0'),
                InlineKeyboardButton('.', callback_data='.'),
                InlineKeyboardButton('Ok', callback_data='Ok'),
            ]
        ]
    )


def bonds_request_callback(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{_get_msg_header(InputStep.FACE_VALUE)}\n{_get_editing_param_title(InputStep.FACE_VALUE)}:',
        reply_markup=get_keyboard()
    )


def keyboard_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    msg_lines = query.message.text.splitlines()
    step = _get_step_by_msg_header(msg_lines[0])
    editing_line = msg_lines[-1]
    pressed_button = query.data

    if pressed_button != 'Ok':
        sep_index = editing_line.find(':')
        new_value = editing_line[sep_index + 2:] + pressed_button
        msg_lines[-1] = f'{editing_line[:sep_index]}: {new_value}'
    else:
        # TODO: validate input
        next_step = _get_next_step(step)
        if next_step != InputStep.END:
            msg_lines[0] = _get_msg_header(next_step)
            msg_lines.append(f'{_get_editing_param_title(next_step)}:')
        else:
            msg_lines[0] = f'Доходность к погашению: {_calc(msg_lines)}%'
            query.edit_message_text(text='\n'.join(msg_lines), reply_markup=None)
            return

    replay_text = '\n'.join(msg_lines)

    query.edit_message_text(
        text=replay_text,
        reply_markup=get_keyboard()
    )


def _calc(msg_lines: List[str]) -> str:
    face_value = float(msg_lines[1][msg_lines[1].find(':') + 1:])
    print(face_value)

    interest_rate = float(msg_lines[2][msg_lines[2].find(':') + 1:]) / 100
    print(interest_rate)

    d, m, y = map(int, msg_lines[3][msg_lines[3].find(':') + 1:].split('.'))
    maturity_date = datetime(y, m, d)
    print(maturity_date)

    price = float(msg_lines[4][msg_lines[4].find(':') + 1:])
    print(price)

    return str(
        get_yield_to_maturity(
            face_value,
            interest_rate,
            y, m, d,
            price
        )
    )
