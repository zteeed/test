import itertools
import json
from functools import partial
from multiprocessing.pool import ThreadPool

from worker import log
from worker.constants import URL
from worker.parser.ctf import is_not_participating, extract_summary, extract_ctf
from worker.parser.profile import extract_pseudo
from worker.redis_interface import session, redis_app


def get_ctf_page(username, page_index):
    url = f'{URL}{username}?inc=ctf&debut_ctf_alltheday_vm_dispo={50 * page_index}#pagination_ctf_alltheday_vm_dispo'
    r = session.get(url)
    if r.status_code != 200:
        log.warning(f'HTTP {r.status_code} for username {username}.')
        return
    return extract_ctf(r.content)


def set_user_ctf(username):
    r = session.get(URL + username + '?inc=ctf')
    if r.status_code != 200:
        log.warning(f'HTTP {r.status_code} for username {username}.')
        return

    if not is_not_participating(r.content):
        log.warning(f'{username} never played CTF all the day.')
        return

    pseudo = extract_pseudo(r.content)
    num_success, num_try = extract_summary(r.content)
    description = f'{num_success} machine(s) compromise(s) en {num_try} tentatives'
    tp_function = partial(get_ctf_page, username)
    nb_ctf_pages = 2  # might need to be changed in some months/years
    tp_argument = list(range(nb_ctf_pages))
    with ThreadPool(nb_ctf_pages) as tp:
        response_ctf = tp.map(tp_function, tp_argument)
    ctfs = list(itertools.chain(response_ctf))  # concatenate all solutions lists

    response = [{
        'pseudo': pseudo,
        'num_success': num_success,
        'num_try': num_try,
        'description': description,
        'ctfs': ctfs,
    }]
    redis_app.set(f'{username}.ctfs', json.dumps(response))
