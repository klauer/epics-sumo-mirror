#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR/.."

PYTHONDIRS="python2 python3"

for d in $PYTHONDIRS; do
    cp -a data $d/sumolib
done
