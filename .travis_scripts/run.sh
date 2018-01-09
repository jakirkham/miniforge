#!/bin/bash

set -ex

conda install -yq constructor jinja2
./build.py --python "${PYVER}" --hash sha256
