#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import os
from os.path import dirname, abspath
import re
import sys
import argparse
import subprocess
import traceback

import lister

from typing import cast, Any, Dict, List, Tuple

RuleList = List[Dict[str, Any]]

exclude = [] # type: List[str]

parser = argparse.ArgumentParser()
parser.add_argument('--full', action='store_true',
    help='Check some things we typically ignore')
args = parser.parse_args()

BASE_DIR = dirname(dirname(abspath(__file__)))
os.chdir(BASE_DIR)

langs = ['py', 'sh', 'json', 'md', 'txt']
by_lang = cast(Dict[str, List[str]], lister.list_files([], ftypes=langs, group_by_ftype=True, exclude=exclude))

# Invoke the appropriate lint checker for each language,
# and also check files for extra whitespace.

def check_pyflakes():
    # type: () -> bool
    failed = False
    if not by_lang['py']:
        return failed
    pyflakes = subprocess.Popen(['pyflakes'] + by_lang['py'],
        stdout = subprocess.PIPE, stderr = subprocess.PIPE,
        universal_newlines = True)

    false_positives = [
        ('imported but unused',),
        ("import *' used; unable to detect undefined names",),
    ] # type: List[Tuple[str, ...]]
    # pyflakes writes some output (like syntax errors) to stderr.
    for pipe in (pyflakes.stdout, pyflakes.stderr):
        for line in pipe:
            fail_line = True
            if not args.full:
                for fp in false_positives:
                    if all((fragment in line for fragment in fp)):
                        fail_line = False
            if fail_line:
                sys.stdout.write(line)
                failed = True
    return failed

def custom_check_file(fpath, rules):
    # type: (str, RuleList) -> bool
    failed = False
    lineFlag = False
    for i, line in enumerate(open(fpath)):
        lineFlag = True
        for rule in rules:
            exclude_list = rule.get('exclude', set())
            if fpath in exclude_list:
                continue
            try:
                if re.search(rule['pattern'], line.strip(rule.get('strip', None))):
                    sys.stdout.write(rule['description'] + ' at %s line %s:\n' % (fpath, i+1))
                    print(line)
                    failed = True
            except Exception:
                print("Exception with %s at %s line %s" % (rule['pattern'], fpath, i+1))
                traceback.print_exc()
        lastLine = line
    if lineFlag and '\n' not in lastLine:
        print("No newline at the end of file " + fpath)
        failed = True
    return failed

whitespace_rules = [
    {'pattern': '\s+$',
     'strip': '\n',
     'description': 'Fix trailing whitespace'},
    {'pattern': '\t',
     'strip': '\n',
     'exclude': set(),
     'description': 'Fix tab-based whitespace'},
] # type: RuleList

rules = {lang: whitespace_rules[:] for lang in langs} # type: Dict[str, RuleList]

rules['py'] += [
    {'pattern': '".*"%\([a-z_].*\)?$',
     'description': 'Missing space around "%"'},
    {'pattern': "'.*'%\([a-z_].*\)?$",
     'description': 'Missing space around "%"'},
    # This rule is constructed with + to avoid triggering on itself
    {'pattern': " =" + '[^ =>~"]',
     'description': 'Missing whitespace after "="'},
    {'pattern': '":\w[^"]*$',
     'description': 'Missing whitespace after ":"'},
    {'pattern': "':\w[^']*$",
     'description': 'Missing whitespace after ":"'},
    {'pattern': "^\s+[#]\w",
     'strip': '\n',
     'description': 'Missing whitespace after "#"'},
    {'pattern': ", [)]",
     'description': 'Unnecessary whitespace between "," and ")"'},
    {'pattern': "%  [(]",
     'description': 'Unnecessary whitespace between "%" and "("'},
    # This next check could have false positives, but it seems pretty
    # rare; if we find any, they can be added to the exclude list for
    # this rule.
    {'pattern': '% [a-zA-Z0-9_.]*\)?$',
     'description': 'Used % comprehension without a tuple'},
]

rules['sh'] += [
    {'pattern': '#!.*sh [-xe]',
     'description': 'Fix shebang line with proper call to /usr/bin/env for Bash path, change -x|-e switches to set -x|set -e'},
]

def check_custom_checks():
    # type: () -> bool
    failed = False
    for lang in langs:
        for fpath in by_lang[lang]:
            if custom_check_file(fpath, rules[lang]):
                failed = True
    return failed

try:
    # Make the lint output bright red
    sys.stdout.write('\x1B[1;31m')
    sys.stdout.flush()

    failed = check_custom_checks()
    failed = check_pyflakes()
    sys.exit(1 if failed else 0)

finally:
    # Restore normal terminal colors
    sys.stdout.write('\x1B[0m')
