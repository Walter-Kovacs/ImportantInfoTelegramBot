import enum
from typing import Protocol

from attrs import define


@define
class HeaderAndContentFactRepr:
    header: str
    content: str


class Fact(Protocol):
    def render_hac(self) -> HeaderAndContentFactRepr:
        pass


class FactGetter(Protocol):
    @classmethod
    def get_important_fact(cls) -> Fact:
        pass
