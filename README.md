[![CircleCI](https://circleci.com/gh/jakirkham/miniforge/tree/master.svg?style=shield)](https://circleci.com/gh/jakirkham/miniforge)
[![Travis CI](https://travis-ci.org/jakirkham/miniforge.svg?branch=master)](https://travis-ci.org/jakirkham/miniforge)
[![AppVeyor](https://ci.appveyor.com/api/projects/status/github/jakirkham/miniforge?svg=True)](https://ci.appveyor.com/project/jakirkham/miniforge/branch/master)

[![Release]( https://img.shields.io/github/release/jakirkham/miniforge.svg "release" )]( https://github.com/jakirkham/miniforge/releases/latest )
[![License]( https://img.shields.io/github/license/jakirkham/miniforge.svg "license" )]( https://raw.githubusercontent.com/jakirkham/miniforge/master/LICENSE.txt )

# About

This provides a `constructor`-based build for a `conda-forge`-based `conda` install that is tested on Linux, macOS, and Windows.


# Usage

To install, please make sure that you have `constructor` 2 installed in `root` of a `conda` install. Then simply run `build.py` to begin. By default it will build an installer using the same version of `python` as is available. However this can be overridden by using the `--python` flag and specifying the major and minor version of `python` to use as either two digits (e.g. `27`) or as a version (e.g. `2.7`). Specifying patch versions are not supported at this time. When a build completes it will be placed in the `out` directory beside `build.py`.
