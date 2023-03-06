from datetime import date
from xml.etree import ElementTree

from telegram import Update
from telegram.ext import CallbackContext

from . import service


def show_main_currencies(update: Update, context: CallbackContext):
    service_response = service.send_request(date.today())
    if service_response.status_code == 200:
        xml_root = ElementTree.fromstring(service_response.text)
        usd = service.get_currency_rate_from_xml('usd', xml_root)
        eur = service.get_currency_rate_from_xml('eur', xml_root)
        cny = service.get_currency_rate_from_xml('cny', xml_root)
        krw = service.get_currency_rate_from_xml('krw', xml_root)

        text = f'{usd[0]} USD = {usd[1]} RUB\n' \
               f'{eur[0]} EUR = {eur[1]} RUB\n' \
               f'{cny[0]} CNY = {cny[1]} RUB\n' \
               f'{krw[0]} KRW = {krw[1]} RUB'
    else:
        text = 'В данный момент не могу узнать курсы валют :('

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
