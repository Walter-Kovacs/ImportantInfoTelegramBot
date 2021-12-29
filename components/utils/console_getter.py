import sys
import random
from components.fact_getters.panorama import PanoramaFactGetter
from components.fact_getters.stub import StubFactGetter
from typing import List
from components.fact_getters.interface import Fact, FactGetter

fact_battarey: List[FactGetter] = [PanoramaFactGetter(), StubFactGetter()]


def print_fact(f: Fact) -> None:
    print('==========================')
    rendered_f = f.render_hac()
    print(f'\n{rendered_f.header}\n')
    print('--------------------------')
    print(f'\n{rendered_f.content}\n')
    print('==========================')


print("Enter command:")
for line in sys.stdin:
    line = line[:-1]
    if line == 'stop':
        break

    fact: Fact = random.choice(fact_battarey).get_important_fact()
    if line == 'fact':
        print("Here is the fact, you asked")
        print_fact(fact)
    else:
        print("Command not recognized. Don't worry, here is important fact for you")
        print_fact(fact)
    print("Enter command:")

print("Process finished")
