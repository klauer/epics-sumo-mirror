#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

# Pypi usage taken from here:
# https://packaging.python.org/guides/migrating-to-pypi-org/

twine upload ../dist/*.tar.gz

# Note: install the package with:
# pip install EPICS-sumo --prefix PREFIX
