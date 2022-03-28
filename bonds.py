from enum import Enum, auto

from components import bonds
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext


class _BondParameter(Enum):
    FACE_VALUE = auto()
    COUPON_RATE = auto()
    MATURITY_DATE = auto()
    PRICE = auto()


class _UnknownBondParameter(Exception):
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


class _Bond:
    def __init__(self):
        self._parameters = {
            _BondParameter.FACE_VALUE: '',
            _BondParameter.COUPON_RATE: '',
            _BondParameter.MATURITY_DATE: '',
            _BondParameter.PRICE: ''
        }
        self._editing_parameter: _BondParameter = _BondParameter.FACE_VALUE

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
    def editing_parameter(self) -> _BondParameter:
        return self._editing_parameter

    @editing_parameter.setter
    def editing_parameter(self, param: _BondParameter):
        self._editing_parameter = param

    def validate_parameter(self, param: _BondParameter) -> bool:
        if param in [_BondParameter.FACE_VALUE, _BondParameter.COUPON_RATE, _BondParameter.PRICE]:
            return _str_is_number(self._parameters[param])
        elif param == _BondParameter.MATURITY_DATE:
            return _str_is_date(self._parameters[param])
        else:
            raise _UnknownBondParameter

    def calc_yield_to_maturity(self) -> float:
        m_day, m_month, m_year = map(int, self._parameters[_BondParameter.MATURITY_DATE].split('.'))

        return bonds.yield_to_maturity(
            float(self._parameters[_BondParameter.FACE_VALUE]),
            float(self._parameters[_BondParameter.COUPON_RATE]),
            m_year, m_month, m_day,
            float(self._parameters[_BondParameter.PRICE])
        )


class _BondUserInterface:
    CALLBACK_PATTERN_EDIT_PARAM = 'bonds_edit_param'
    CALLBACK_PATTERN_SELECT_PARAM = 'bonds_select_param'
    _edit_param_keyboard: InlineKeyboardMarkup = None
    _select_param_keyboard: InlineKeyboardMarkup = None
    _editing_msg_header = {
        _BondParameter.FACE_VALUE: 'Введите номинал облигации',
        _BondParameter.COUPON_RATE: 'Введите купон в процентах',
        _BondParameter.MATURITY_DATE: 'Введите дату погашения в формате дд.мм.гггг',
        _BondParameter.PRICE: 'Введите рыночную цену'
    }
    _select_param_header = 'Выберите параметр облигации для редактирования'
    _param_title = {
        _BondParameter.FACE_VALUE: 'Номинал',
        _BondParameter.COUPON_RATE: 'Купон, %',
        _BondParameter.MATURITY_DATE: 'Дата погашения',
        _BondParameter.PRICE: 'Цена'
    }

    def __init__(self, chat_id: int, msg_id: int):
        self._chat_id = chat_id
        self._msg_id = msg_id
        self._bond = _Bond()
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
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{_BondParameter.FACE_VALUE.name}'
                    ),
                    InlineKeyboardButton(
                        'Купон',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{_BondParameter.COUPON_RATE.name}'
                    )
                ],
                [
                    InlineKeyboardButton(
                        'Дата погашения',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{_BondParameter.MATURITY_DATE.name}'
                    ),
                    InlineKeyboardButton(
                        'Цена',
                        callback_data=f'{cls.CALLBACK_PATTERN_SELECT_PARAM}{_BondParameter.PRICE.name}'
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
        for param in _BondParameter:
            lines.append(f'{cls._param_title[param]}:')
        return '\n'.join(lines)

    def get_select_param_msg_text(self) -> str:
        lines = [self._select_param_header]
        for param in _BondParameter:
            lines.append(f'{self._param_title[param]}: {self._bond.parameters[param]}')
        return '\n'.join(lines)

    def get_editing_params_msg_text(self) -> str:
        lines = [self._editing_msg_header[self._bond.editing_parameter]]
        for param in _BondParameter:
            lines.append(f'{self._param_title[param]}: {self._bond.parameters[param]}')
        return '\n'.join(lines)

    def get_final_msg_text(self, yield_to_maturity: float) -> str:
        lines = [f'Доходность к погашению: {str(yield_to_maturity)}%']
        for param in _BondParameter:
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
        for param in _BondParameter:
            if not self._bond.validate_parameter(param):
                return False
        return True


_bonds_UIs = dict()


def start_callback(update: Update, context: CallbackContext):
    message = context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=_BondUserInterface.get_start_msg_text(),
        reply_markup=_BondUserInterface.get_select_param_keyboard()
    )

    chat_id = update.effective_chat.id
    msg_id = message.message_id
    _bonds_UIs[f'{chat_id}|{msg_id}'] = _BondUserInterface(chat_id, msg_id)


def keyboard_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    message = query.message
    try:
        ui_id = f'{update.effective_chat.id}|{message.message_id}'
        ui: _BondUserInterface = _bonds_UIs[ui_id]
    except KeyError:
        query.edit_message_text(text='Начните с начала')
        return

    query_data = query.data
    if query_data.startswith(_BondUserInterface.CALLBACK_PATTERN_SELECT_PARAM):
        pressed_button = query_data.lstrip(_BondUserInterface.CALLBACK_PATTERN_SELECT_PARAM)
        if pressed_button == 'Calc':
            if ui.validate_all():
                query.edit_message_text(
                    text=ui.get_final_msg_text(ui.bond.calc_yield_to_maturity())
                )
                _bonds_UIs.pop(ui_id)
            else:
                if ui.prev_pressed_button != 'Calc':
                    query.edit_message_text(
                        text=f'Не все параметры заполнены корректно\n{ui.get_select_param_msg_text()}',
                        reply_markup=ui.get_select_param_keyboard()
                    )
        else:  # parameter
            ui.bond.editing_parameter = _BondParameter[pressed_button]
            query.edit_message_text(
                text=ui.get_editing_params_msg_text(),
                reply_markup=ui.get_edit_param_keyboard()
            )
    else:
        pressed_button = query_data.lstrip(_BondUserInterface.CALLBACK_PATTERN_EDIT_PARAM)
        if pressed_button == 'Ok':
            if ui.prev_pressed_button != 'Ok':
                if ui.bond.validate_parameter(ui.bond.editing_parameter):
                    query.edit_message_text(
                        text=ui.get_select_param_msg_text(),
                        reply_markup=ui.get_select_param_keyboard()
                    )
                else:
                    query.edit_message_text(
                        text=f'Неверное значение параметра\n{ui.get_editing_params_msg_text()}',
                        reply_markup=ui.get_edit_param_keyboard()
                    )
        elif pressed_button == 'Del':
            if ui.bond.del_symbol():
                query.edit_message_text(
                    text=ui.get_editing_params_msg_text(),
                    reply_markup=ui.get_edit_param_keyboard()
                )
        else:  # . or digit
            ui.bond.append_symbol(pressed_button)
            query.edit_message_text(
                text=ui.get_editing_params_msg_text(),
                reply_markup=ui.get_edit_param_keyboard()
            )

    ui.prev_pressed_button = pressed_button
