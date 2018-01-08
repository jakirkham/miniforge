#!/bin/bash

set -x

conda install -yq constructor jinja2

/home/conda/repo/build.py --python "${PYVER}" --hash md5 sha1 sha256
