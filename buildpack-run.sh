#!/bin/bash

# Reconstruct repo locally
git --version
git init
git remote add origin https://github.com/jakirkham/miniforge.git
git fetch origin
git checkout -fq "$SOURCE_VERSION"

# Construct dummy git user
git config --global user.name "Your Name"
git config --global user.email "you@example.com"

# Get token
export GH_TOKEN="$(cat $ENV_DIR/GH_TOKEN)"

# Publish release
python release.py --tag --remote origin --publish prerelease
