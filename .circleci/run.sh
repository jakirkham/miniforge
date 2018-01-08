#!/bin/bash

set -ex

conda install -yq constructor jinja2

/home/conda/repo/distclean.py
/home/conda/repo/build.py --python "${PYVER}" --hash md5 sha1 sha256
/home/conda/repo/check.py out/miniforge-py${PYVER}-*.sh
/home/conda/repo/distclean.py
