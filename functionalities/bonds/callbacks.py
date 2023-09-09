from telegram import Update
from telegram.ext import ContextTypes

from functionalities.bonds.interface import (
    BondUserInterface,
    bonds_UIs,
    BondParameter,
)


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=BondUserInterface.get_start_msg_text(),
        reply_markup=BondUserInterface.get_select_param_keyboard()
    )

    chat_id = update.effective_chat.id
    msg_id = message.message_id
    bonds_UIs[f'{chat_id}|{msg_id}'] = BondUserInterface(chat_id, msg_id)


async def keyboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    message = query.message
    try:
        ui_id = f'{update.effective_chat.id}|{message.message_id}'
        ui: BondUserInterface = bonds_UIs[ui_id]
    except KeyError:
        await query.edit_message_text(text='Начните с начала')
        return

    query_data = query.data
    if query_data.startswith(BondUserInterface.CALLBACK_PATTERN_SELECT_PARAM):
        pressed_button = query_data.lstrip(BondUserInterface.CALLBACK_PATTERN_SELECT_PARAM)
        if pressed_button == 'Calc':
            if ui.validate_all():
                await query.edit_message_text(
                    text=ui.get_final_msg_text(ui.bond.calc_yield_to_maturity())
                )
                bonds_UIs.pop(ui_id)
            else:
                if ui.prev_pressed_button != 'Calc':
                    await query.edit_message_text(
                        text=f'Не все параметры заполнены корректно\n{ui.get_select_param_msg_text()}',
                        reply_markup=ui.get_select_param_keyboard()
                    )
        else:  # parameter
            ui.bond.editing_parameter = BondParameter[pressed_button]
            await query.edit_message_text(
                text=ui.get_editing_params_msg_text(),
                reply_markup=ui.get_edit_param_keyboard()
            )
    else:
        pressed_button = query_data.lstrip(BondUserInterface.CALLBACK_PATTERN_EDIT_PARAM)
        if pressed_button == 'Ok':
            if ui.prev_pressed_button != 'Ok':
                if ui.bond.validate_parameter(ui.bond.editing_parameter):
                    await query.edit_message_text(
                        text=ui.get_select_param_msg_text(),
                        reply_markup=ui.get_select_param_keyboard()
                    )
                else:
                    await query.edit_message_text(
                        text=f'Неверное значение параметра\n{ui.get_editing_params_msg_text()}',
                        reply_markup=ui.get_edit_param_keyboard()
                    )
        elif pressed_button == 'Del':
            if ui.bond.del_symbol():
                await query.edit_message_text(
                    text=ui.get_editing_params_msg_text(),
                    reply_markup=ui.get_edit_param_keyboard()
                )
        else:  # . or digit
            ui.bond.append_symbol(pressed_button)
            await query.edit_message_text(
                text=ui.get_editing_params_msg_text(),
                reply_markup=ui.get_edit_param_keyboard()
            )

    ui.prev_pressed_button = pressed_button
