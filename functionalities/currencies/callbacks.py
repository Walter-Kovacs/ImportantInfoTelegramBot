import datetime

from telegram import Update
from telegram.ext import CallbackContext

from .services import binance
from .services import cbr


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

    rates = cbr.get_currencies_rates(date, *codes)
    if len(rates) == 0:
        text = 'Не могу узнать курс валюты :('
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


def start_with_keyword_callback(update: Update, context: CallbackContext):
    currency = update.message.text.split(maxsplit=1)[1]  # message text: "курс <валюты>"
    code = cbr.currencies.codes_by_phrase.get(currency.lower())
    if code is not None:
        rate = cbr.get_currencies_rates(datetime.date.today(), code)
        if len(rate) > 0:
            rate = rate[code]
            text = f'{rate[0]} {code} = {rate[1]} RUB'
        else:
            text = 'Не могу узнать курс валюты :('
    else:
        text = 'Не могу узнать курс валюты :('

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )


def bitcoin_rate_callback(update: Update, context: CallbackContext):
    try:
        btc_busd: float = binance.get_btc_busd_rate()
        usd_rub_info: tuple = cbr.get_currencies_rates(datetime.date.today(), 'USD')['USD']
        usd_rub_amount, usd_rub_rate = int(usd_rub_info[0]), float(usd_rub_info[1])
        btc_rub = btc_busd * (usd_rub_rate / usd_rub_amount)
        text = f'1 BTC = {format(btc_busd, "_.2f").replace("_", " ")} BUSD\n' \
               f'1 BTC = {format(btc_rub, "_.2f").replace("_", " ")} RUB'
    except binance.ServiceError:
        text = 'Не могу узнать курс :('

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )
