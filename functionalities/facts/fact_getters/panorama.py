import enum
import random
import re
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional, Tuple

import requests
from attrs import Factory, define, field

from functionalities.facts.fact_getters.interface import Fact, HeaderAndContentFactRepr


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

empty_data_re = re.compile(r'^\s+$', flags=re.MULTILINE)


@define
class PageParser(HTMLParser):
    article_number: int
    debug: bool = Factory(bool)

    article_time: Optional[str] = field(default=None)
    article_href: Optional[str] = field(default=None)

    _articles_div_stack: int = Factory(bool)
    _article_count: int = Factory(int)

    _current_action: str = field(default='search_for_articles_div')
    _data_catcher: Optional[Callable[[str], bool]] = Factory(lambda: None)

    def __attrs_post_init__(self):
        super().__init__()

    def _debug(self, *args):
        if self.debug:
            print(args)

    @classmethod
    def _get_attr(cls, attrs: List[Tuple[str, str]], key: str) -> Optional[str]:
        for attr in attrs:
            if attr[0] == key:
                return attr[1]
        return None

    def handle_starttag(self, tag, attrs):
        self._debug(tag, attrs, self._current_action)
        if self._current_action == 'go_to_finish':
            return

        if self._current_action == 'search_for_articles_div':
            cl = self._get_attr(attrs, 'class')
            if cl is not None and cl == 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-5 gap-x-2.5 gap-y-4 lg:gap-y-2.5':
                self._current_action = 'pass_to_certain_article'
            return

        self._articles_div_stack += 1
        if self._current_action == 'pass_to_certain_article':
            if self._articles_div_stack == 1 and tag == 'a':
                self._article_count += 1
                if self._article_count == self.article_number:
                    self.article_href = self._get_attr(attrs, 'href')
                    # self._current_action = 'search_for_date'
                    self._current_action = 'go_to_finish'
            if self._articles_div_stack <= 0:
                raise Exception(
                    f'PageParser: pass_to_certain_article failed: articles_div_passed, article_count: {self._article_count}, article_number {self.article_number}'
                )
            return

        # Not used in this version
        if self._current_action == 'search_for_date':
            if self._articles_div_stack <= 0:
                raise Exception('PageParser: search_for_date failed: articles_div_passed')
            self._debug('search_for_date: ', tag, attrs)
            if tag == 'span' and (self._get_attr(attrs, 'class') or '') == 'date':

                def dc(data):
                    if empty_data_re.match(data):
                        return False
                    if '::before' in data:
                        return False
                    self.article_time = data.strip()
                    return True

                self._data_catcher = dc
                self._current_action = 'go_to_finish'
            return

        raise Exception(f'PageParser error: unknown _current_action of parser {self._current_action}')

    def handle_endtag(self, tag):
        if self._current_action in ['go_to_finish', 'search_for_articles_div']:
            return

        self._articles_div_stack -= 1

    def handle_data(self, data):
        if self._data_catcher is None:
            return
        self._debug('Catching data: ', data)

        all_catched = self._data_catcher(data)
        if all_catched:
            self._data_catcher = None


@define
class PanoramaFact:
    article_type: ArticleType
    article_publication_time: str  # Not used in this version
    article_link: str

    def render_hac(self) -> HeaderAndContentFactRepr:
        return HeaderAndContentFactRepr(
            header=f'<b>{header_map[self.article_type]}</b>',
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
        if pp.article_href is None:
            raise Exception(
                'some information not found in panorama response'
                + f'found href: {pp.article_href}'
            )
        return PanoramaFact(
            article_type=at,
            article_link=f'https://{cls.panorama_url}{pp.article_href}',
            article_publication_time=pp.article_time,
        )

    @classmethod
    def get_important_fact(cls):
        return cls._get_fact_from_panorama(random.choice(cls.article_types), random.randint(1, 6))
