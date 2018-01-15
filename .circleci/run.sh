#!/bin/bash

set -ex
export PYTHONUNBUFFERED=1

conda install -yq constructor jinja2

/home/conda/repo/distclean.py
/home/conda/repo/build.py --python "${PYVER}" --hash sha256
/home/conda/repo/check.py "/home/conda/repo/out/miniforge-py${PYVER}-*.sh"

if [ "$CIRCLE_PULL_REQUEST" != "" ]; then
    /home/conda/repo/distclean.py
fi

mkdir -p out
