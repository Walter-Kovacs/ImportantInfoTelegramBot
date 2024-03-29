import logging
import random
from typing import List

from .fact_getters import currencies
from .fact_getters import time
from .fact_getters.interface import Fact, FactGetter
from .fact_getters.panorama import PanoramaFactGetter
from .fact_getters.stub import StubFact

fact_battery: List[FactGetter] = [
    PanoramaFactGetter(),
    currencies.RateFactGetter(),
    time.TimeFactGetter(),
]

log = logging.getLogger('random_fact_skill')


def fact_to_message(f: Fact) -> str:
    rendered_f = f.render_hac()
    return f"{rendered_f.header}\n\n{rendered_f.content}"


def get_random_important_fact() -> str:
    try:
        f: Fact = random.choice(fact_battery).get_important_fact()
    except Exception as e:
        log.error(f'failed to get random_fact; exception: {e}')
        f = StubFact()

    return fact_to_message(f)
