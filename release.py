#!/usr/bin/env python

import argparse
import codecs
import contextlib
import json
import os
import shlex
import subprocess
import sys

try:
    from urllib.error import HTTPError
    from urllib.request import (
        Request,
        urlopen,
    )
except ImportError:
    from urllib2 import (
        HTTPError,
        Request,
        urlopen,
    )


def is_valid_url(url):
    try:
        with contextlib.closing(urlopen(url)) as response:
            return True
    except HTTPError:
        return False


def request_json(url, data=None, headers={}):
    if data:
        data = json.dumps(data)
    request = Request(url, data, headers=headers)
    with contextlib.closing(urlopen(request)) as response:
        reader = codecs.getreader("utf-8")
        return json.load(reader(response))


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
        "--tag",
        action="store_true",
        help="Whether to tag or not."
    )
    parser.add_argument(
        "--remote",
        help="Specify a remote for pushing and/or publishing."
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Optionally push to specified remote."
    )
    parser.add_argument(
        "--publish",
        choices=["prerelease", "final"],
        help="Optionally publish the final release on GitHub."
    )
    args = parser.parse_args(args=argv[1:])

    base_dir = os.path.dirname(os.path.abspath(__file__))
    _scripts_dir = os.path.join(base_dir, ".scripts")

    version = subprocess.check_output(
        [sys.executable, os.path.join(_scripts_dir, "version.py")],
        universal_newlines=True
    ).strip()

    if args.push and not args.remote:
        raise RuntimeError("Need a remote to push.")

    if args.publish:
        if not args.remote:
            raise RuntimeError("Need a remote to publish.")

        if "GH_TOKEN" not in os.environ:
            raise RuntimeError(
                "Set `GH_TOKEN` environment variable to publish."
            )

        remote_url = subprocess.check_output(
            ["git", "remote", "get-url", args.remote],
            universal_newlines=True
        ).strip()

        if "github.com" not in remote_url:
            raise RuntimeError("Publishing only works with GitHub.")

        repo_slug = remote_url.split(".git")[0].split("github.com")[1][1:]

        if not is_valid_url("https://github.com/%s" % repo_slug):
            raise RuntimeError("Found invalid repo slug: %s" % repo_slug)

    if args.remote:
        subprocess.call(
            ["git", "fetch", args.remote, version],
            universal_newlines=True
        )

    if args.tag:
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

    if args.push:
        subprocess.check_call(
            shlex.split(
                "git push {force} {remote} {tag}".format(
                    force=args.force, remote=args.remote, tag=version
                )
            ),
            universal_newlines=True
        )

    if args.publish:
        prerelease = (args.publish == "prerelease")
        try:
            release = request_json(
                (
                    "https://api.github.com/repos/%s/releases/tags/%s" %
                    (repo_slug, version)
                ),
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": "token %s" % os.environ["GH_TOKEN"]
                }
            )
            release_id = release["id"]

            request_json(
                (
                    "https://api.github.com/repos/%s/releases/%i"
                    % (repo_slug, release_id)
                ),
                data={
                    "prerelease": prerelease
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": "token %s" % os.environ["GH_TOKEN"]
                }
            )
        except HTTPError:
            commit_msg = subprocess.check_output(
                ["git", "log", "--format=%B", "-n", "1", version],
                universal_newlines=True
            ).strip()

            version_sha1 = subprocess.check_output(
                ["git", "rev-list", "-n", "1", version],
                universal_newlines=True
            ).strip()

            request_json(
                (
                    "https://api.github.com/repos/%s/releases"
                    % repo_slug
                ),
                data={
                    "tag_name": version,
                    "target_commitish": version_sha1,
                    "name": version,
                    "body": commit_msg,
                    "prerelease": prerelease
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.github.v3+json",
                    "Authorization": "token %s" % os.environ["GH_TOKEN"]
                }
            )


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
