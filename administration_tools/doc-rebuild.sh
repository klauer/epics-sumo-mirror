#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=`dirname "$ME"`

cd "$MYDIR/../doc"

./make-png.sh
make clean -s
make html

$MYDIR/mk-sumo-doc.sh
