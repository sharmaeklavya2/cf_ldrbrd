#!/usr/bin/env python

import json
import requests
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

class Contest:
    name = '' # type: str
    phase = '' # type: str

    def __init__(self, contest):
        # type: (Mapping[str, Any]) -> None
        self.name = contest["name"]
        self.phase = contest["phase"]

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
        self.points = problem["points"]
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

class CfApiError(Exception):
    response = None # type: Optional[requests.Response]
    http_error = None # type: Optional[requests.exceptions.HTTPError]

    def __init__(self, response, http_error=None):
        # type: (requests.Response, Optional[requests.exceptions.HTTPError]) -> None
        self.response = response
        self.http_error = http_error

def get_contest_info(contest_id, usernames, show_unofficial):
    # type: (int, Iterable[str], bool) -> Tuple[Contest, List[Problem], List[Participant]]

    query = {
        'contestId': contest_id,
        'handles': ';'.join(usernames),
        'showUnofficial': 'true' if show_unofficial else 'false',
    } # type: Dict[str, Any]

    response = requests.get('http://codeforces.com/api/contest.standings', params=query)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_error:
        raise CfApiError(response, http_error)
    response_json = response.json()
    if response_json["status"] != 'OK':
        raise CfApiError(response)
    result = response_json["result"]

    contest = Contest(result["contest"])
    problems = [Problem(prob) for prob in result["problems"]]
    participants = [Participant(row) for row in result["rows"]]

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
