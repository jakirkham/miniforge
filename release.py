#!/usr/bin/env python

import argparse
import os
import shlex
import subprocess
import sys


def main(*argv):
    parser = argparse.ArgumentParser(
        description="Prep a release of the `conda-forge`-based installer."
    )
    parser.add_argument(
        "-f", "--force", action="store_const",
        default="", const="--force",
        help="Forcibly tag and push (if `--push` given)."
    )
    parser.add_argument(
        "--push", metavar="<remote>", dest="remote",
        help="Optionally push to specified remote."
    )
    args = parser.parse_args(args=argv[1:])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    _scripts_dir = os.path.join(base_dir, ".scripts")

    version = subprocess.check_output(
        [sys.executable, os.path.join(_scripts_dir, "version.py")],
        universal_newlines=True
    ).strip()

    if args.remote:
        subprocess.call(
            ["git", "fetch", args.remote, version],
            universal_newlines=True
        )

    subprocess.check_call(
        shlex.split(
            "git tag {force} -a {tag} -m {tag}".format(
                force=args.force, tag=version
            )
        ),
        universal_newlines=True
    )

    subprocess.check_call(
        ["git", "--no-pager", "show", version],
        universal_newlines=True
    )

    if args.remote:
        subprocess.check_call(
            shlex.split(
                "git push {force} {remote} {tag}".format(
                    force=args.force, remote=args.remote, tag=version
                )
            ),
            universal_newlines=True
        )


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
