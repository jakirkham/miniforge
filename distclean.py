#!/usr/bin/env python

import argparse
import os
import shutil
import sys


def main(*argv):
    parser = argparse.ArgumentParser(
        description="Cleanup any installers in `out`."
    )
    args = parser.parse_args(args=argv[1:])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(base_dir, "out")

    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
