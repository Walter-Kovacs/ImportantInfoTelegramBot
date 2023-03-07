import logging
from datetime import date
from xml.etree import ElementTree

from telegram import Update
from telegram.ext import CallbackContext

from . import service


logger = logging.getLogger(__name__)


def show_main_currencies(update: Update, context: CallbackContext):
    cannot_get_rate_text = 'В данный момент не могу узнать курсы валют :('

    service_response = service.send_request(date.today())
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
