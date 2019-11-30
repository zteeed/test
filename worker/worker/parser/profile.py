from html import unescape

from lxml import html

from worker.constants import URL
from worker.parser.exceptions import RootMeParsingError


def extract_pseudo(content: bytes) -> str:
    tree = html.fromstring(content)
    result = tree.xpath('string(//span[@class=" forum"])')
    if not result:
        raise RootMeParsingError()
    return unescape(result)


def extract_score(content: bytes) -> int:
    tree = html.fromstring(content)
    result = tree.xpath('string(//div[@class="small-3 columns text-center"][2]/h3)')[1:]
    if not result:  # Manage case when score is null (score is not displayed on profile)
        return 0
    if not result:  # result can be equal to '' with this xpath search
        raise RootMeParsingError()
    result = int(result)
    return result


def extract_avatar_url(content: bytes) -> str:
    tree = html.fromstring(content)
    result = tree.xpath('string(//img[@class="vmiddle logo_auteur logo_6forum"]/@src)')
    if not result:
        raise RootMeParsingError()
    return f'{URL}/{result}'
