import re
from html import unescape

from lxml import html

from worker.zip import zip_equal


def extract_stats(content):
    tree = html.fromstring(content)
    javascript_text = tree.xpath('//script[@type="text/javascript"]/text()')[-1]
    pattern = r'evolution_data_total.push\(new Array\("(.*?)",(\d+), "(.*?)", "(.*?)"\)\)'
    challenges_solved = re.findall(pattern, javascript_text)
    pattern = r'validation_totale\[(\d+)\]\+\=1;'
    difficulties = re.findall(pattern, javascript_text)
    result = []
    for challenge_data, difficulty in zip_equal(challenges_solved, difficulties):
        date, score_at_date, name, path = challenge_data
        challenge = {
            'name': unescape(name),
            'score_at_date': int(score_at_date),
            'date': date,
            'path': path,
            'difficulty': int(difficulty),
        }
        result.append(challenge)
    return result
