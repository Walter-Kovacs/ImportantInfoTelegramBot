import requests
import enum
import random
from attrs import define, Factory, field
from typing import List, Dict, Optional, Callable, Tuple
from components.fact_getters.interface import HeaderAndContentFactRepr, Fact
from html.parser import HTMLParser


class ArticleType(enum.Enum):
    Politics = 'politics'
    Society = 'society'
    Science = 'science'
    Economics = 'economics'


header_map: Dict[ArticleType, str] = {
    ArticleType.Politics: 'Новости политики',
    ArticleType.Society: 'Новости мирового сообщества',
    ArticleType.Science: 'Новости с острия науки',
    ArticleType.Economics: 'Политэкономическая ситуация',
}


@define
class PageParser(HTMLParser):
    article_number: int

    article_time: Optional[str] = field(default=None)
    article_href: Optional[str] = field(default=None)

    _in_articles_div: bool = Factory(bool)
    _articles_div_stack: int = Factory(bool)
    _article_count: int = Factory(int)
    _articles_div_passed: bool = Factory(bool)

    _current_action: str = field(default='search_for_articles_div')
    _data_catcher: Optional[Callable[[str], bool]] = Factory(lambda: None)

    @classmethod
    def _get_attr(cls, attrs: List[Tuple[str, str]], key: str) -> Optional[str]:
        for attr in attrs:
            if attr[0] == key:
                return attr[1]
        return None

    def handle_starttag(self, tag, attrs):
        if self._current_action == 'go_to_finish':
            return

        if self._current_action == 'search_for_articles_div':
            cl = self._get_attr(attrs, 'class')
            if cl is not None and al == 'news big-previews two-in-row':
                self._at_articles_div = True
            return

        self._articles_div_stack += 1
        if self._current_action == 'pass_to_certain_article':
            if self._articles_div_stack == 1 and tag == 'a':
                self._article_count += 1
                if self.article_count == self.article_number:
                    self.article_href = self.get_attr(attrs, 'href')
                    self._current_action = 'search_for_date'
            if self._articles_div_stack <= 0:
                raise Exception(
                    'PageParser: pass_to_certain_article failed: articles_div_passed, article_count: {self._article_count}, article_number {self.article_number}'
                )
            return

        if self._current_action == 'search_for_date':
            if self._articles_div_stack <= 0:
                raise Exception('PageParser: search_for_date failed: articles_div_passed')
            if tag == 'span' and (self._get_attr(attrs, 'class') or '') == 'date':

                def dc(data):
                    if '::before' in data:
                        return False
                    self.article_time = data
                    return True

                self._data_catcher = dc
                self._current_action = 'go_to_finish'
            return

        raise Exception(f'PageParser error: unknown _current_action of parser {self._current_action}')

    def handle_endtag(self, tag):
        if self._current_action == 'go_to_finish':
            return

        self._articles_div_stack -= 1
        if self._articles_div_stack == 0:
            self._articles_div_passed = True

    def handle_data(self, data):
        if self._data_catcher is None:
            return

        all_catched = self._data_catcher(data)
        if all_catched:
            self._data_catcher = None


@define
class PanoramaFact:
    article_type: ArticleType
    article_publication_time: str
    article_link: str

    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header=header_map[self.article_type] + f' ({self.article_publication_time} время московское)',
            content=self.article_link,
        )


class PanoramaFactGetter:
    article_types: List[ArticleType] = list(ArticleType)
    panorama_url: str = 'panorama.pub'

    @classmethod
    def _get_fact_from_panorama(cls, at: ArticleType, number: int) -> Fact:
        resp = requests.get(f'https://{cls.panorama_url}/{at.value}')
        if resp.status_code != 200:
            raise Exception(f'Failed to load panorama content {resp.status_code}')

        pp = PageParser(article_number=number)
        pp.feed(resp.text)
        pp.close()
        if pp.article_href is None or pp.article_time is None:
            raise Exception('some information not found in panorama response')
        return PanoramaFact(article_type=at, article_link=pp.article_href, article_publication_time=pp.article_time)

    @classmethod
    def get_important_fact(cls):
        return cls._get_fact_from_panorama(random.choice(cls.article_types), random.randint(1, 6))
