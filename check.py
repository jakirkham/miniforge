#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import glob
import os
import subprocess
import sys


def git_commit_time(ref="HEAD"):
    git_time_str = subprocess.check_output(
        ["git", "show", "-s", "--format=%ci", ref],
        universal_newlines=True
    )
    git_time_str = git_time_str.strip()
    git_utctime = datetime.datetime.strptime(
        git_time_str[:19] + " UTC",
        "%Y-%m-%d %H:%M:%S %Z"
    )

    git_timedelta = datetime.timedelta()
    if len(git_time_str) > 19:
        git_timedelta = datetime.datetime.strptime(git_time_str[21:], "%H%M")
        git_timedelta = datetime.timedelta(
            hours=git_timedelta.hour, minutes=git_timedelta.minute
        )
        if git_time_str[20] == "-":
            git_timedelta = -git_timedelta

    git_time = git_utctime - git_timedelta

    return git_time


def main(*argv):
    exit_code = 0

    parser = argparse.ArgumentParser(
        description="Create a `conda-forge`-based installer."
    )
    parser.add_argument(
        "installers",
        nargs="+",
        help="Installer(s) to test"
    )
    args = parser.parse_args(args=argv[1:])

    base_dir = os.path.dirname(os.path.abspath(__name__))

    all_installer_fns = []
    for each_installer_fn in args.installers:
        all_installer_fns.extend(glob.iglob(each_installer_fn))

    for each_installer_fn in all_installer_fns:
        each_installer_fn = os.path.abspath(each_installer_fn)
        print("Testing installer: %s" % each_installer_fn)

        print("Verifying installer version...", end="")
        git_time_str = git_commit_time(ref="HEAD").strftime("%Y%m%dT%H%M%SZ")
        if git_time_str in each_installer_fn:
            print("PASS")
        else:
            exit_code = 1
            print("FAIL")

    return(exit_code)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
