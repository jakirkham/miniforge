#!/usr/bin/env python

from __future__ import print_function

import argparse
import glob
import os
import sys


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

    return(exit_code)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
