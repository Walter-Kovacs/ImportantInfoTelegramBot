from enum import Enum, auto

from . import calculation
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class BondParameter(Enum):
    FACE_VALUE = auto()
    COUPON_RATE = auto()
    MATURITY_DATE = auto()
    PRICE = auto()


class UnknownBondParameter(Exception):
    pass


def _str_is_number(s: str) -> bool:
    if len(s) == 0:
        return False

    fraction_point_counter = 0
    for ch in s:
        if ch not in '.0123456789':
            return False
        if ch == '.':
            fraction_point_counter += 1

    if fraction_point_counter in [0, 1]:
        return True
    else:
        return False


def _str_is_date(s: str) -> bool:  # dd.mm.yyyy
    parts = s.split('.')
    if len(parts) != 3:
        return False

    day, month, year = parts
    if len(day) != 2 or len(month) != 2 or len(year) != 4:
        return False
    if not _str_is_number(day) or not _str_is_number(month) or not _str_is_number(year):
        return False
    return True


class Bond:
    def __init__(self):
        self._parameters = {
            BondParameter.FACE_VALUE: '',
            BondParameter.COUPON_RATE: '',
            BondParameter.MATURITY_DATE: '',
            BondParameter.PRICE: ''
        }
        self._editing_parameter: BondParameter = BondParameter.FACE_VALUE

    def append_symbol(self, char: str):
        self._parameters[self._editing_parameter] += char

    def del_symbol(self) -> bool:
        current_value = self._parameters[self._editing_parameter]
        if len(current_value) > 0:
            self._parameters[self._editing_parameter] = current_value[:len(current_value) - 1]
            return True
        else:
            return False

    @property
    def parameters(self):
        return self._parameters

    @property
    def editing_parameter(self) -> BondParameter:
        return self._editing_parameter

    @editing_parameter.setter
    def editing_parameter(self, param: BondParameter):
        self._editing_parameter = param

    def validate_parameter(self, param: BondParameter) -> bool:
        if param in [BondParameter.FACE_VALUE, BondParameter.COUPON_RATE, BondParameter.PRICE]:
            return _str_is_number(self._parameters[param])
        elif param == BondParameter.MATURITY_DATE:
            return _str_is_date(self._parameters[param])
        else:
            raise UnknownBondParameter

    def calc_yield_to_maturity(self) -> float:
        m_day, m_month, m_year = map(int, self._parameters[BondParameter.MATURITY_DATE].split('.'))

        return calculation.yield_to_maturity(
            float(self._parameters[BondParameter.FACE_VALUE]),
            float(self._parameters[BondParameter.COUPON_RATE]),
            m_year, m_month, m_day,
            float(self._parameters[BondParameter.PRICE])
        )


class BondUserInterface:
    CALLBACK_PATTERN_EDIT_PARAM = 'bonds_edit_param'
    CALLBACK_PATTERN_SELECT_PARAM = 'bonds_select_param'
    _edit_param_keyboard: InlineKeyboardMarkup = None
    _select_param_keyboard: InlineKeyboardMarkup = None
    _editing_msg_header = {
        BondParameter.FACE_VALUE: 'Введите номинал облигации',
        BondParameter.COUPON_RATE: 'Введите купон в процентах',
        BondParameter.MATURITY_DATE: 'Введите дату погашения в формате дд.мм.гггг',
        BondParameter.PRICE: 'Введите рыночную цену'
    }
    _select_param_header = 'Выберите параметр облигации для редактирования'
    _param_title = {
        BondParameter.FACE_VALUE: 'Номинал',
        BondParameter.COUPON_RATE: 'Купон, %',
        BondParameter.MATURITY_DATE: 'Дата погашения',
        BondParameter.PRICE: 'Цена'
    }

    def __init__(self, chat_id: int, msg_id: int):
        self._chat_id = chat_id
        self._msg_id = msg_id
        self._bond = Bond()
        self._prev_pressed_button = ''
        self._init_keyboards()

    @classmethod
    def _init_keyboards(cls):
        if cls._edit_param_keyboard is not None and cls._select_param_keyboard is not None:
            return

        cls._edit_param_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('7', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}7'),
                    InlineKeyboardButton('8', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}8'),
                    InlineKeyboardButton('9', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}9'),
                ],
                [
                    InlineKeyboardButton('4', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}4'),
                    InlineKeyboardButton('5', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}5'),
                    InlineKeyboardButton('6', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}6'),
                ],
                [
                    InlineKeyboardButton('1', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}1'),
                    InlineKeyboardButton('2', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}2'),
                    InlineKeyboardButton('3', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}3'),
                ],
                [
                    InlineKeyboardButton('0', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}0'),
                    InlineKeyboardButton('.', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}.'),
                    InlineKeyboardButton('Del', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}Del'),
                    InlineKeyboardButton('Ok', callback_data=f'{cls.CALLBACK_PATTERN_EDIT_PARAM}Ok')
                ],
            ]
        )

        cls._select_param_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        'Номинал',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{BondParameter.FACE_VALUE.name}'
                    ),
                    InlineKeyboardButton(
                        'Купон',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{BondParameter.COUPON_RATE.name}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Дата погашения',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{BondParameter.MATURITY_DATE.name}'
                    ),
                    InlineKeyboardButton(
                        'Цена',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{BondParameter.PRICE.name}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Рассчитать',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}Calc'
                    )
                ]
            ]
        )

    @classmethod
    def get_edit_param_keyboard(cls) -> InlineKeyboardMarkup:
        cls._init_keyboards()
        return cls._edit_param_keyboard

    @classmethod
    def get_select_param_keyboard(cls) -> InlineKeyboardMarkup:
        cls._init_keyboards()
        return cls._select_param_keyboard

    @classmethod
    def get_start_msg_text(cls):
        lines = [cls._select_param_header]
        for param in BondParameter:
            lines.append(f'{cls._param_title[param]}:')
        return '\n'.join(lines)

    def get_select_param_msg_text(self) -> str:
        lines = [self._select_param_header]
        for param in BondParameter:
            lines.append(f'{self._param_title[param]}: {self._bond.parameters[param]}')
        return '\n'.join(lines)

    def get_editing_params_msg_text(self) -> str:
        lines = [self._editing_msg_header[self._bond.editing_parameter]]
        for param in BondParameter:
            lines.append(f'{self._param_title[param]}: {self._bond.parameters[param]}')
        return '\n'.join(lines)

    def get_final_msg_text(self, yield_to_maturity: float) -> str:
        lines = [f'Доходность к погашению: {str(yield_to_maturity)}%']
        for param in BondParameter:
            lines.append(f'{self._param_title[param]}: {self._bond.parameters[param]}')
        return '\n'.join(lines)

    @property
    def bond(self):
        return self._bond

    @property
    def prev_pressed_button(self) -> str:
        return self._prev_pressed_button

    @prev_pressed_button.setter
    def prev_pressed_button(self, button: str):
        self._prev_pressed_button = button

    def validate_all(self) -> bool:
        for param in BondParameter:
            if not self._bond.validate_parameter(param):
                return False
        return True


bonds_UIs = dict()
