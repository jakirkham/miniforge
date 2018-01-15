#!/usr/bin/env python

from __future__ import print_function

import argparse
import contextlib
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile


@contextlib.contextmanager
def mkdtemp(*args, **kwargs):
    tmp_dir = tempfile.mkdtemp(*args, **kwargs)
    yield tmp_dir
    shutil.rmtree(tmp_dir)


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

    base_dir = os.path.dirname(os.path.abspath(__file__))
    checks_dir = os.path.join(base_dir, "checks")
    specs_dir = os.path.join(base_dir, "src", "specs")

    all_installer_fns = []
    for each_installer_fn in args.installers:
        all_installer_fns.extend(glob.iglob(each_installer_fn))

    for each_installer_fn in all_installer_fns:
        each_installer_fn = os.path.abspath(each_installer_fn)
        print("Testing installer: %s" % each_installer_fn)

        print("Verifying installer version...", end="")

        cwd = os.getcwd()
        try:
            os.chdir(base_dir)
            git_time_str = git_commit_time(ref="HEAD").strftime("%Y%m%dT%H%M%SZ")
        finally:
            os.chdir(cwd)

        if git_time_str in each_installer_fn:
            print("PASS")
        else:
            exit_code = 1
            print("FAIL")

        with mkdtemp(prefix="miniforge_") as tmp_dir:
            print("Created temp directory: %s" % tmp_dir)

            script_ext = os.extsep
            installer_ext = os.extsep
            if sys.platform == "win32":
                script_ext += "bat"
                installer_ext += "exe"
            else:
                script_ext += "sh"
                installer_ext += "sh"

            shutil.copy(
                os.path.join(checks_dir, "check%s" % script_ext),
                tmp_dir
            )

            tmp_installer_fn = os.path.join(
                tmp_dir, "miniforge" + installer_ext
            )
            shutil.copy(each_installer_fn, tmp_installer_fn)

            print("Shelling out for further testing.")
            cwd = os.getcwd()
            try:
                os.chdir(tmp_dir)
                if sys.platform == "win32":
                    subprocess.check_call(
                        ["check%s" % script_ext]
                    )
                else:
                    subprocess.check_call([
                        "bash",
                        "check%s" % script_ext
                    ])
            finally:
                with open("info.json", "r") as fh:
                    res_info = json.load(fh)

                res_spec = []
                with open("spec.txt", "r") as fh:
                    for l in fh:
                        if not l.startswith("#"):
                            res_spec.append(tuple(l.split()[:3]))
                res_spec = tuple(res_spec)

                os.chdir(cwd)
                print("Cleaning up.")

        print("Comparing installer specs...", end="")

        res_platform = res_info["platform"]
        res_py = "".join(res_info["python_version"].split(".")[:2])

        fn_spec = "%s_py%s.txt" % (res_platform, res_py)
        fn_spec = os.path.join(specs_dir, fn_spec)

        exp_spec = []
        with open(fn_spec, "r") as fh:
            for l in fh:
                exp_spec.append(tuple(l.split()[:3]))
        exp_spec = tuple(exp_spec)

        if res_spec == exp_spec:
            print("PASS")
        else:
            exit_code = 1
            print("FAIL")

    return(exit_code)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
