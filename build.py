#!/usr/bin/env python

import argparse
import contextlib
import hashlib
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
    parser.add_argument(
        "--hash",
        type=str,
        nargs="*",
        default=[],
        dest="hash_names",
        help="Hashes to run on each installer"
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

    hash_names = args.hash_names
    for hn in hash_names:
        hashlib.new(hn)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base_dir, "src")
    _scripts_dir = os.path.join(base_dir, ".scripts")

    out_dir = os.path.join(base_dir, "out")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    git_time_str = subprocess.check_output(
        [sys.executable, os.path.join(_scripts_dir, "version.py")],
        universal_newlines=True
    ).strip()

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

        if hash_names:
            for fn in os.listdir(out_tmp_dir):
                fn = os.path.join(out_tmp_dir, fn)
                if os.path.isfile(fn):
                    print(
                        "Computing hashes for \"%s\"." % os.path.basename(fn)
                    )

                    fn_hashes = {}
                    for hn in hash_names:
                        h = subprocess.check_output(
                            ["openssl", hn, fn],
                            universal_newlines=True
                        )
                        h = h.split()[-1]
                        fn_hashes[hn] = h

                    print("Writing out hashes.")
                    for hn in hash_names:
                        h = fn_hashes[hn]
                        with open(fn + os.extsep + hn, "w") as fh:
                            fh.write(h)
                            fh.write("\n")

        for each_fn in os.listdir(out_tmp_dir):
            each_fn = os.path.join(out_tmp_dir, each_fn)
            shutil.move(each_fn, out_dir)

        print("Moved installer to: %s" % out_dir)


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
