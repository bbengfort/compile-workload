#!/usr/bin/env python3
# workload
# Run a compiler workload and evaluate external performance of a file system.
#
# Author:   Benjamin Bengfort <benjamin@bengfort.com>
# Created:  Tue Jan 24 10:36:01 2017 -0500
#
# Copyright (C) 2016 Bengfort.com
# For license information, see LICENSE.txt
#
# ID: workload.py [] benjamin@bengfort.com $

"""
Runs a compiler workload against the given directory.
"""

##########################################################################
## Imports
##########################################################################

import os
import csv
import time
import json
import shutil
import argparse

from functools import wraps
from subprocess import call
from os.path import join, getsize


##########################################################################
## Projects and Results Keys
##########################################################################

PROJECTS = {
    'redis': {
        "repo": "git@github.com:antirez/redis.git",
        "cmds": [
            ["make"],
        ]
    },
    'postgres': {
        "repo": "git@github.com:postgres/postgres.git",
        "cmds": [
            ["./configure"],
            ["make"],
        ]
    },
    'nginx': {
        "repo": "git@github.com:nginx/nginx.git",
        "cmds": [
            ["./auto/configure"],
            ["make"],
        ]
    },
    'apache': {
        "repo": "git@github.com:apache/httpd.git",
        "cmds": [
            ["git", "clone", "git@github.com:apache/apr.git", "srclib/apr"],
            ["./buildconf"],
            ["./configure", "--with-included-apr"],
            ["make"],
        ]
    },
    'ruby': {
        "repo": "git@github.com:ruby/ruby.git",
        "cmds": [
            ["autoconf"],
            ["./configure"],
            ["make"],
        ]
    },
    'python': {
        "repo": "git@github.com:python/cpython.git",
        "cmds": [
            ["./configure"],
            ["make"],
        ]
    },
}

## Results Keys
TEST_NAME   = "test name"
TEST_PATH   = "test path"
CLONE_TIME  = "clone time"
CLONE_STAT  = "clone stat"
CLONE_BYTES = "clone bytes"
CLONE_FILES = "clone files"
CLONE_DIRS  = "clone dirs"
BUILD_TIME  = "build time"
BUILD_STAT  = "build stat"
BUILD_BYTES = "build bytes"
BUILD_FILES = "build files"
BUILD_DIRS  = "build dirs"


## Key lists
TEST_RESULTS  = [TEST_NAME, TEST_PATH, CLONE_TIME, BUILD_TIME]
CLONE_RESULTS = [CLONE_STAT, CLONE_BYTES, CLONE_FILES, CLONE_DIRS]
BUILD_RESULTS = [BUILD_STAT, BUILD_BYTES, BUILD_FILES, BUILD_DIRS]


##########################################################################
## Helper Functions
##########################################################################

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        started = time.time()
        result = func(*args, **kwds)
        return result, time.time() - started
    return wrapper


def withcwd(func):
    @wraps(func)
    def wrapper(*args, **kwds):
        cwd = os.getcwd()
        try:
            return func(*args, **kwds)
        finally:
            os.chdir(cwd)
    return wrapper


@timeit
def statdir(path):
    """
    Walks a directory and returns the number of files, bytes, and time
    required to walk the directory.
    """
    n_bytes = 0
    n_files = 0
    n_dirs  = 0

    for root, dirs, files in os.walk(path):
        n_bytes += sum(getsize(join(root, name)) for name in files)
        n_files += len(files)
        n_dirs  += len(dirs)

    return n_bytes, n_files, n_dirs


@timeit
def clone(repo, path):
    """
    Run git clone on the repo url to the specified path.
    """
    call(["git", "clone", repo, path])


@timeit
@withcwd
def build(cmds, path):
    """
    Run the build commands in the specified directory
    """
    # change directories to the path
    os.chdir(path)

    # run the build commands
    for cmd in cmds:
        call(cmd)


##########################################################################
## Run Workload
##########################################################################

def run_workload(path, project='redis', output='results.csv', header=False):
    """
    Conducts the clone, compile, and stat workload in the given path and for
    the given project, which must be one of the listed projects. Results are
    then written to the path specified by output.
    """
    # Make sure the path exists
    if not os.path.exists(path) or not os.path.isdir(path):
        raise TypeError("{} must be an existing directory!".format(path))

    # Make sure the directory is empty
    if len(os.listdir(path)) > 0:
        raise ValueError("{} is not empty!".format(path))

    # Get the project details and commands
    if project not in PROJECTS:
        raise ValueError("unknown project '{}'".format(project))
    commands = PROJECTS[project]

    # Create the results object
    results = {
        TEST_NAME: project,
        TEST_PATH: path
    }

    # Clone the repository
    _, results[CLONE_TIME] = clone(commands["repo"], join(path, project))

    # Stat the directory after cloning
    (size, files, dirs), time = statdir(path)
    for key, val in zip(CLONE_RESULTS, [time, size, files, dirs]):
        results[key] = val

    # Build the project
    _, results[BUILD_TIME] = build(commands["cmds"], join(path, project))

    # Stat the directory after building
    (size, files, dirs), time = statdir(path)
    for key, val in zip(BUILD_RESULTS, [time, size, files, dirs]):
        results[key] = val

    # Write the results to disk
    with open(output, 'a') as fobj:
        fields = TEST_RESULTS + CLONE_RESULTS + BUILD_RESULTS
        writer = csv.DictWriter(fobj, fieldnames=fields)

        if header: writer.writeheader()
        writer.writerow(results)

    # Clean up the data in the specified path
    shutil.rmtree(join(path, project))

    # Print the results from the workload
    print(json.dumps(results, indent=2))

##########################################################################
## Main and Argument Parsing
##########################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="run a compiler workload and evaluate performance",
        epilog="submit issues to github.com/bbengfort/compile-workload",
    )

    parser.add_argument(
        'path', nargs=1, metavar='PATH', help='location to run evaluation'
    )

    parser.add_argument(
        '-o', '--output', metavar='CSV', type=str, default='results.csv',
        help='csv file to append results to.'
    )

    parser.add_argument(
        '-p', '--project', choices=PROJECTS.keys(), type=str, default='redis',
        help='project to clone and compile', metavar='NAME'
    )

    parser.add_argument(
        '-H', '--header', action='store_true', default=False,
        help='write the header row to the results file'
    )

    args = parser.parse_args()
    try:
        run_workload(args.path[0], args.project, args.output, args.header)
        parser.exit(0)
    except Exception as e:
        parser.error(str(e))
