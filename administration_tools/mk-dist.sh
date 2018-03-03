#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

set -e
cd "$MYDIR/.."
python setup.py sdist --formats=zip,gztar
