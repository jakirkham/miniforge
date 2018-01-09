#!/usr/bin/env python

import argparse
import codecs
import contextlib
import glob
import json
import os
import mmap
import subprocess
import sys

try:
    from urllib.request import (
        Request,
        urlopen,
    )
except ImportError:
    from urllib2 import (
        Request,
        urlopen,
    )


def request_json(url, data=None, headers={}):
    request = Request(url, data, headers=headers)
    with contextlib.closing(urlopen(request)) as response:
        reader = codecs.getreader("utf-8")
        return json.load(reader(response))


def main(*argv):
    parser = argparse.ArgumentParser(
        description="Prep a release of the `conda-forge`-based installer."
    )
    parser.add_argument(
        "--repo", required=True, help="Repo to publish to."
    )
    parser.add_argument(
        "--upload", metavar="<files>", dest="filenames",
        nargs="+",
        help="Names of files to publish to the release."
    )
    args = parser.parse_args(args=argv[1:])

    if "GH_TOKEN" not in os.environ:
        raise RuntimeError(
            "Set `GH_TOKEN` environment variable to publish."
        )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    _scripts_dir = os.path.join(base_dir, ".scripts")

    repo = args.repo
    version = subprocess.check_output(
        [sys.executable, os.path.join(_scripts_dir, "version.py")],
        universal_newlines=True
    ).strip()

    subprocess.call(
        ["git", "fetch", "https://github.com/%s.git" % repo, version],
        universal_newlines=True
    )

    release_info = request_json(
        (
            "https://api.github.com/repos/%s/releases/tags/%s" %
            (repo, version)
        ),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token %s" % os.environ["GH_TOKEN"]
        }
    )
    release_upload_url = release_info["upload_url"].split("{?name,label}")[0]

    for each_glob_filename in args.filenames:
        for each_filename in glob.iglob(each_glob_filename):
            with open(each_filename, "rb") as fh:
                with contextlib.closing(mmap.mmap(fh.fileno(), 0, access=mmap.ACCESS_READ)) as fmm:
                    each_filename = os.path.basename(each_filename)
                    request = Request(
                        release_upload_url + "?name=%s" % each_filename,
                        fmm,
                        headers={
                            "Content-Type": "application/octet-stream",
                            "Accept": "application/vnd.github.v3+json",
                            "Authorization": (
                                "token %s" % os.environ["GH_TOKEN"]
                            ),
                            "name": each_filename
                        }
                    )
                    with contextlib.closing(urlopen(request)) as response:
                        reader = codecs.getreader("utf-8")
                        json_resp = json.load(reader(response))


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
