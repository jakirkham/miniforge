#!/bin/bash

set -x

conda install -yq constructor jinja2
./build.py --python "${PYVER}"
