#!/usr/bin/env python

import argparse
import datetime
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
    parser = argparse.ArgumentParser(
        description="Generate version from commit time."
    )

    git_time_str = git_commit_time(ref="HEAD").strftime("%Y%m%dT%H%M%SZ")

    print(git_time_str)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
