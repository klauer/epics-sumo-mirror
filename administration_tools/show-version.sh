#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

PYTHONPATH=.. python3 ../bin/sumo --version
