from components.fact_getters.interface import Fact, HeaderAndContentFactRepr


class StubFact:
    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header="Заголовок важного факта",
            content="Суть важного факта",
        )


class StubFactGetter:
    @classmethod
    def get_important_fact(cls) -> Fact:
        return StubFact()
