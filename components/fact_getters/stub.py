from components.fact_getters.interface import Fact, HeaderAndContentFactRepr


class StubFact:
    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header="Внимание!",
            content="Важных фактов не нашлось",
        )


class StubFactGetter:
    @classmethod
    def get_important_fact(cls) -> Fact:
        return StubFact()
