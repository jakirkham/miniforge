#!/bin/bash

source deactivate

set -x

bash miniforge.sh -b -p ./prefix

source ./prefix/bin/activate

conda info

conda list

source deactivate
