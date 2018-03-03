#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR/.."

for f in ../python2/bin/*; do
        sed -i '1 s/python2.5\>/python/' $f
done
