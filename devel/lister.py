#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import os
from os.path import abspath
import subprocess
from collections import defaultdict
import argparse
from typing import Union, List, Dict

def get_ftype(fpath):
    # type: (str) -> str
    ext = os.path.splitext(fpath)[1]
    return ext[1:]

def list_files(targets=[], ftypes=[], exclude=[], group_by_ftype=False):
    # type: (List[str], List[str], List[str], bool) -> Union[Dict[str, List[str]], List[str]]
    """
    List files tracked by git.
    Returns a list of files which are either in targets or in directories in targets.
    If targets is [], list of all tracked files in current directory is returned.

    Other arguments:
    ftypes - List of file types on which to filter the search.
        If ftypes is [], all files are included.
    exclude - List of paths to be excluded.
    group_by_ftype - If True, returns a dict of lists keyed by file type.
        If False, returns a flat list of files.
    """
    ftypes = [x.lstrip('.') for x in ftypes]
    ftypes_set = set(ftypes)

    cmdline = ['git', 'ls-files'] + targets

    files_gen = (x.strip() for x in subprocess.check_output(cmdline, universal_newlines=True).split('\n'))
    # throw away empty lines and non-files (like symlinks)
    files = [f for f in files_gen if os.path.isfile(f)]

    result_dict = defaultdict(list) # type: Dict[str, List[str]]
    result_list = [] # type: List[str]

    for fpath in files:
        # this will take a long time if exclude is very large
        in_exclude = False
        absfpath = abspath(fpath)
        for expath in exclude:
            expath = abspath(expath.rstrip('/'))
            if absfpath == expath or absfpath.startswith(expath + '/'):
                in_exclude = True
        if in_exclude:
            continue

        if ftypes or group_by_ftype:
            filetype = get_ftype(fpath)
            if ftypes and filetype not in ftypes_set:
                continue

        if group_by_ftype:
            result_dict[filetype].append(fpath)
        else:
            result_list.append(fpath)

    if group_by_ftype:
        return result_dict
    else:
        return result_list

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="List files tracked by git and optionally filter by type")
    parser.add_argument('targets', nargs='*', default=[],
                        help='''files and directories to include in the result.
                        If this is not specified, the current directory is used''')
    parser.add_argument('-f', '--ftypes', nargs='+', default=[],
                        help="list of file types to filter on. All files are included if this option is absent")
    parser.add_argument('--exclude', nargs='+', default=[],
                        help='list of files and directories to exclude from listing')
    args = parser.parse_args()
    listing = list_files(targets=args.targets, ftypes=args.ftypes, exclude=args.exclude)
    for l in listing:
        print(l)
