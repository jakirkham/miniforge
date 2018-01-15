#!/bin/bash

source deactivate

set -x

bash miniforge.sh -b -p ./prefix

source ./prefix/bin/activate

conda info

conda info --json > info.json

conda list | tee spec.txt

conda update -c conda-forge --quiet --dry-run --all

source deactivate
