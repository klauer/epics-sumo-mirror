#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

PYTHONPATH=../python2 python2 ../python2/bin/sumo --version
PYTHONPATH=../python3 python3 ../python3/bin/sumo --version
