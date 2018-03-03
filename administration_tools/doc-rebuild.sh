#!/bin/sh

MYDIR=`dirname "$0"`

cd "$MYDIR/../doc"

./make-png.sh
make clean -s
make html
