#!/usr/bin/env python

import json
import requests
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

BASE_URL = 'http://codeforces.com/api'

class Contest:
    name = '' # type: str
    phase = '' # type: str
    type = '' # type: str

    def __init__(self, contest):
        # type: (Mapping[str, Any]) -> None
        self.name = contest["name"]
        self.phase = contest["phase"]
        self.type = contest["type"]

    def __str__(self) -> str:
        return "Contest({}, {})".format(repr(self.name), self.phase)
    def __repr__(self) -> str:
        return str(self)

class Problem:
    name = '' # type: str
    index = '' # type: str
    points = 0.0 # type: float

    def __init__(self, problem):
        # type: (Mapping[str, Any]) -> None
        self.name = problem["name"]
        self.points = problem.get("points", 0)
        self.index = problem["index"]

    def __str__(self) -> str:
        return "Problem({})".format(self.points)
    def __repr__(self) -> str:
        return str(self)

class Attempt:
    # An attempt is a set of submissions to a particular problem by a particular user
    points = 0.0 # type: float
    rejects = 0 # type: int

    def __init__(self, problem_result):
        # type: (Mapping[str, Any]) -> None
        self.points = problem_result["points"]
        self.rejects = problem_result["rejectedAttemptCount"]

    def __str__(self) -> str:
        return 'Attempt({}, {})'.format(self.points, self.rejects)
    def __repr__(self) -> str:
        return str(self)

class Participant:
    username = '' # type: str
    type = '' # type: str
    rank = 0 # type: int
    points = 0.0 # type: float
    attempts = [] # type: List[Attempt]
    color = '' # type: str

    def __init__(self, ranklist_row):
        # type: (Mapping[str, Any]) -> None
        self.type = ranklist_row["party"]["participantType"]
        self.rank = ranklist_row["rank"]
        self.points = ranklist_row["points"]
        self.attempts = [Attempt(att) for att in ranklist_row["problemResults"]]
        self.username = ranklist_row["party"].get("teamName") or ranklist_row["party"]["members"][0]["handle"]

    def __str__(self) -> str:
        return 'Participant({}, {})'.format(self.username, self.type)
    def __repr__(self) -> str:
        return str(self)

class CfUser:
    username = '' # type: str
    first_name = '' # type: str
    last_name = '' # type: str
    rating = 0 # type: int
    color = '' # type: str

    rank_to_color = {
        "legendary grandmaster": "lgm",
        "international grandmaster": "igm",
        "grandmaster": "gm",
        "international master": "im",
        "master": "master",
        "candidate master": "cm",
        "expert": "expert",
        "specialist": "specialist",
        "pupil": "pupil",
        "newbie": "newbie",
    }

    def __init__(self, userinfo):
        # type: (Mapping[str, Any]) -> None
        self.username = userinfo['handle']
        self.first_name = userinfo.get('firstName', '')
        self.last_name = userinfo.get('lastName', '')
        self.rating = userinfo.get('rating', 0)
        self.color = self.rank_to_color.get(userinfo.get('rank', ''), '')

    def __str__(self) -> str:
        return 'CfUser({})'.format(self.username)
    def __repr__(self) -> str:
        return str(self)

class CfApiError(Exception):
    response = None # type: Optional[requests.Response]
    http_error = None # type: Optional[requests.exceptions.HTTPError]

    def __init__(self, response, http_error=None):
        # type: (requests.Response, Optional[requests.exceptions.HTTPError]) -> None
        self.response = response
        self.http_error = http_error

def log_and_request(**kwargs):
    # type: (**Any) -> requests.Response
    prequest = requests.Request('GET', **kwargs).prepare()
    print('GET', prequest.url)
    with requests.Session() as session:
        response = session.send(prequest)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        raise CfApiError(response, http_error)
    if response.json()["status"] != 'OK':
        raise CfApiError(response)

    return response

def get_user_info(usernames):
    # type: (Iterable[str]) -> List[CfUser]
    query = {'handles': ';'.join(usernames)}
    response = log_and_request(url = BASE_URL + '/user.info', params=query)
    result = response.json()["result"]

    return [CfUser(userinfo) for userinfo in result]

def get_contest_info(contest_id, usernames, show_unofficial):
    # type: (int, Iterable[str], bool) -> Tuple[Contest, List[Problem], List[Participant]]

    query = {
        'contestId': contest_id,
        'handles': ';'.join(usernames),
        'showUnofficial': 'true' if show_unofficial else 'false',
    } # type: Dict[str, Any]

    response = log_and_request(url = BASE_URL + '/contest.standings', params=query)

    result = response.json()['result']
    contest = Contest(result["contest"])
    problems = [Problem(prob) for prob in result["problems"]]
    participants = [Participant(row) for row in result["rows"]]

    try:
        userlist = get_user_info(usernames)
        colormap = {user.username: user.color for user in userlist}
        for p in participants:
            p.color = colormap.get(p.username, '')
    except CfApiError:
        pass

    return (contest, problems, participants)

def main():
    # type: () -> None
    contest_id = int(input("Enter contest ID: "))
    usernames = input("Enter space separated usernames: ").split()

    contest, problems, participants = get_contest_info(contest_id, usernames, True)

    print(contest)
    print(problems)
    for p in participants:
        print(p)
        print('\t' + str(p.attempts))

if __name__ == "__main__":
    main()
