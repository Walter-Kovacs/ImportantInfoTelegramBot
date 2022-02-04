import random
from typing import List

from components.fact_getters.interface import Fact, FactGetter
from components.fact_getters.panorama import PanoramaFactGetter
from components.fact_getters.stub import StubFactGetter

fact_battery: List[FactGetter] = [PanoramaFactGetter(), StubFactGetter()]


def fact_to_message(f: Fact) -> str:
    rendered_f = f.render_hac()
    return f"""==========================
    \n{rendered_f.header}\n
    '--------------------------
    \n{rendered_f.content}\n
    '==========================
    """


def get_random_important_fact() -> str:
    f: Fact = random.choice(fact_battery).get_important_fact()
    return fact_to_message(f)
