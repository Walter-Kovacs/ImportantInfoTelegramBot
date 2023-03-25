import random

from .interface import HeaderAndContentFactRepr
import functionalities.facts.time as time


class TimeFact:
    def __init__(self, time_fact: str):
        self.time_fact = time_fact

    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header=self.time_fact,
            content='',
        )


class TimeFactGetter:
    @classmethod
    def get_important_fact(cls) -> TimeFact:
        time_func = random.choice([getattr(time, func_name) for func_name in time.__all__])
        return TimeFact(time_func())
