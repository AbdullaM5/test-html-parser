import re
from typing import Iterable, Tuple, Optional

from bs4 import BeautifulSoup


class Extractor:
    def __call__(self, html: str) -> str:
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup(['script', 'style']):
            tag.decompose()

        non_break_space = '\xa0'
        line_break = '\n'
        text: str = soup \
            .find('body') \
            .get_text(separator=' ', strip=True) \
            .replace(non_break_space, ' ') \
            .replace(line_break, ' ')

        text = re.sub(' +', ' ', text)

        return text


class Finder:
    pattern = re.compile(
        r'(?P<prefix>\w+)?[\s]'
        r'(?P<country>\+7|8)?[\s]?[(|-]?'
        r'(?P<city>\d{3})?[-|)]?[\s]?'
        r'(?P<number>\d{3}[\s|-]?\d{2}[\s|-]?\d{2})'
    )

    def __call__(self, text: str):
        return self.pattern.findall(text)


class Filter:
    stop_prefixes = ['ИНН', 'ОГРН']

    def __call__(self, results: Iterable[Tuple[str, str, str, str]]) -> Iterable[Tuple[str, str, str, str]]:
        return filter(lambda x: x[0] not in self.stop_prefixes, results)


class Formatter:
    @staticmethod
    def _process_phone_number(prefix: str, country: str, code: str, number: str) -> str:
        country = '+7' if country == '' else country
        country = '+7' if country == '8' else country
        code = '495' if code == '' else code
        number = number.replace('-', '').replace(' ', '')
        return ''.join([country, code, number])

    def __call__(self, results: Iterable[Tuple[str, str, str]]) -> Iterable[str]:
        return [self._process_phone_number(*result) for result in results]


class Parser:
    extractor_class = Extractor
    finder_class = Finder
    filter_class = Filter
    formatter_class = Formatter

    def __init__(self):
        self.extractor = self.extractor_class()
        self.finder = self.finder_class()
        self.filter = self.filter_class()
        self.formatter = self.formatter_class()
        self.callable_chain = [self.extractor, self.finder, self.filter, self.formatter]

    @staticmethod
    def _deduplicate(results: Iterable[str]) -> Iterable[str]:
        return list(set(results))

    def __call__(self, value: str) -> Optional[Iterable[str]]:
        for callable_ in self.callable_chain:
            value = callable_(value)
        result = self._deduplicate(value)
        return result
