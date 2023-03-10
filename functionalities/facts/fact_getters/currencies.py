import datetime
import random
from typing import Dict, Tuple

from .interface import HeaderAndContentFactRepr
from functionalities.currencies.services import cbr


class RateFact:
    def __init__(self, currency_name, currency_code, amount, rate):
        self.currency_name = currency_name
        self.currency_code = currency_code
        self.amount = amount
        self.rate = rate

    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header=f'Курс {self.currency_name} на сегодня',
            content=f'{self.amount} {self.currency_code} = {self.rate} RUB',
        )


class RateFactGetter:
    @classmethod
    def get_important_fact(cls) -> RateFact:
        currencies = cbr.currencies.codes_by_phrase
        currency = random.choice(list(currencies.keys()))
        currency_code = currencies[currency]

        rates: Dict[str, Tuple[str, str]] = cbr.get_currencies_rates(datetime.date.today(), currency_code)
        amount, rate = rates[currency_code]

        return RateFact(
            currency_name=currency,
            currency_code=currency_code,
            amount=amount,
            rate=rate,
        )
