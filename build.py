#!/usr/bin/env python

import argparse
import contextlib
import datetime
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap


@contextlib.contextmanager
def mkdtemp(*args, **kwargs):
    tmp_dir = tempfile.mkdtemp(*args, **kwargs)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


def rmmkdir(dn):
    if os.path.exists(dn):
        shutil.rmtree(dn)
    os.makedirs(dn)


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


def write_jinja_vars(fn, dct):
    txt = ""
    for k, v in dct.items():
        txt += textwrap.dedent(
            """\
            {{% set {0} = "{1}" %}}
            """.format(k, v)
        )

    with open(fn, "w") as fh:
        fh.write(txt)


def main(*argv):
    parser = argparse.ArgumentParser(
        description="Create a `conda-forge`-based installer."
    )
    parser.add_argument(
        "--python",
        default="%i.%i" % (sys.version_info.major, sys.version_info.minor),
        type=str,
        help="Python version to use in install"
    )
    args = parser.parse_args(args=argv[1:])

    py_ver = []
    if "." in args.python:
        py_ver = args.python.split(".")
    else:
        py_ver = list(args.python)

    if len(py_ver) != 2:
        raise RuntimeError("Python version should be two values.")

    py_ver_maj = py_ver[0]
    py_ver_min = py_ver[1]

    base_dir = os.path.dirname(os.path.abspath(__name__))
    src_dir = os.path.join(base_dir, "src")

    out_dir = os.path.join(base_dir, "out")
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    git_time_str = git_commit_time(ref="HEAD").strftime("%Y%m%dT%H%M%SZ")

    with mkdtemp(prefix="miniforge_") as tmp_dir:
        print("Created temp directory: %s" % tmp_dir)

        build_dir = os.path.join(tmp_dir, "build")
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        shutil.copytree(src_dir, build_dir)

        shutil.copy(os.path.join(base_dir, "LICENSE.txt"), build_dir)

        write_jinja_vars(
            os.path.join(build_dir, "version.jinja"),
            dict(
                version=git_time_str
            )
        )

        write_jinja_vars(
            os.path.join(build_dir, "python.jinja"),
            dict(
                py_ver_maj=py_ver_maj,
                py_ver_min=py_ver_min,
            )
        )

        cache_dir = os.path.join(tmp_dir, "cache")
        rmmkdir(cache_dir)

        out_tmp_dir = os.path.join(tmp_dir, "out")
        rmmkdir(out_tmp_dir)

        subprocess.check_call([
            "constructor",
            "--debug",
            build_dir,
            "--output-dir", out_tmp_dir,
            "--cache-dir", cache_dir
        ])

        shutil.move(out_tmp_dir, out_dir)

        print("Moved installer to: %s" % out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
