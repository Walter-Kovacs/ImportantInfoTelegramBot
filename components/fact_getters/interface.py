import attr
import enum
from typing import Protocol

@attr.s
class HeaderAndContentFactRepr:
    header: str = attr.ib()
    content: str = attr.ib()

class Fact(Protocol):
    def render_hac(self) -> HeaderAndContentFactRepr:
        pass

class FactGetter(Protocol):
    @classmethod
    def get_important_fact(cls) -> Fact:
        pass
