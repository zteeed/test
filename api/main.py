#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import math
import re

import requests as rq
from flask import redirect, jsonify

from api import repeater
from api.app import app
from api.cache_wrapper import cached
from api.constants import REFRESH_CACHE_INTERVAL, AUTHORS, ENDPOINTS, GITHUB_ACCOUNTS
from api.http_interface.challenges import get_all_challenges
from api.http_interface.profile import get_user_profile
from api.http_interface.contributions import get_user_contributions
from api.http_interface.details import get_user_details
from api.http_interface.ctf import get_user_ctf


@app.route("/")
@cached(timeout=math.inf)  # Never timeout, this is static.
def root():
    return jsonify(title="Root-Me-API",
                   authors=AUTHORS,
                   follow_us=GITHUB_ACCOUNTS,
                   paths=ENDPOINTS)


@app.route("/challenges")
def challenges():
    return jsonify(get_all_challenges_cached())


@app.route("/<username>")
def get_user(username):
    return redirect('/{}/profile'.format(username), code=302)


@cached(timeout = 10)
@app.route('/<username>/profile')
def get_profile(username):
    return jsonify(get_user_profile(username))


@cached(timeout = 10)
@app.route('/<username>/contributions')
def get_contributions(username):
    return jsonify(get_user_contributions(username))


@cached(timeout = 10)
@app.route('/<username>/details')
def get_score(username):
    return jsonify(get_user_details(username))


@app.route('/<username>/ctf')
def get_ctf(username):
    return jsonify(get_user_ctf(username))


@app.route('/<username>/stats')
def get_stats(username):
    r = rq.get(URL + username + '?inc=statistiques')
    if r.status_code != 200: return r.text, r.status_code
    txt = r.text.replace('\n', '')
    txt = txt.replace('&nbsp;', '')
    pattern = '<meta name="author" content="(.*?)"/>'
    exp = re.findall(pattern, txt)
    if not exp: return '', 500
    pseudo = exp[0]

    """ Evolution du Score """
    pattern = '<script type="text/javascript">(.*?)</script>'
    exp = re.findall(pattern, txt)
    exp = ''.join(exp)
    pattern = 'evolution_data_total.push\(new Array\("(.*?)",(\d+), "(.*?)", "(.*?)"\)\)'
    pattern += 'validation_totale\[(\d+)\]\+\=1;'
    challenges_solved = re.findall(pattern, exp)
    challenges = dict()
    for id, challenge_solved in enumerate(challenges_solved):
        challenge = dict()
        (date, score, name, path, difficulty) = challenge_solved
        challenge = dict(name=name, score=score, path=path,
                         difficulty=difficulty, date=date)
        challenges[id] = challenge
    send = dict(pseudo=pseudo, challenges=challenges)
    return json.dumps(send, ensure_ascii=False).encode('utf8'), 200


@cached(key_prefix="challenges")
def get_all_challenges_cached():
    return get_all_challenges()


def update_endpoints():
    get_all_challenges_cached(cache_refresh=True)
    app.logger.info("/challenges cache updated")


if __name__ == "__main__":
    repeater.start(update_endpoints, REFRESH_CACHE_INTERVAL)
    app.run(host='0.0.0.0', debug=True, use_reloader=False)
    repeater.stop()
