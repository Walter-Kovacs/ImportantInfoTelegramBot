import logging
import datetime
from xml.etree import ElementTree

from telegram import Update
from telegram.ext import CallbackContext

from .services.cbr import get_currencies_rates, service

logger = logging.getLogger(__name__)


def currency_command_callback(update: Update, context: CallbackContext):
    args = context.args
    if len(args) == 0:
        codes = ('USD', 'EUR', 'CNY', 'KRW')
        date = datetime.date.today()
    elif len(args) == 1:
        codes = (args[0].upper(), )
        date = datetime.date.today()
    else:
        codes = (args[0].upper(), )
        try:
            date = datetime.date.fromisoformat(args[1])
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='Некорректный формат даты. Введите дату в формате гггг-мм-дд',
            )
            return

    rates = get_currencies_rates(date, *codes)
    if len(rates) == 0:
        text = 'В данный момент не могу узнать курсы валют :('
    else:
        result = []
        for code in codes:
            if code in rates:
                rate = rates[code]
                result.append(f'{rate[0]} {code} = {rate[1]} RUB')
        text = '\n'.join(result)
        if date != datetime.date.today():
            text = f'Курс на {date}:\n' + text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )


def show_main_currencies(update: Update, context: CallbackContext):
    cannot_get_rate_text = 'В данный момент не могу узнать курсы валют :('

    service_response = service.send_request(datetime.date.today())
    if service_response.status_code == 200:
        xml_root = ElementTree.fromstring(service_response.text)
        try:
            codes = ['USD', 'EUR', 'CNY', 'KRW']
            rates = [
                (
                    code,
                    service.get_currency_rate_from_xml(code, xml_root)
                ) for code in codes
            ]

            result = []
            for code, rate in rates:
                if rate is not None:
                    result.append(f'{rate[0]} {code} = {rate[1]} RUB')
                else:
                    logger.warning(f'Unknown currency code: {code}')

            if len(result) > 0:
                text = '\n'.join(result)
            else:
                text = cannot_get_rate_text

        except service.ServiceChanged as e:
            logger.warning(e)
            text = cannot_get_rate_text
    else:
        text = cannot_get_rate_text

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
