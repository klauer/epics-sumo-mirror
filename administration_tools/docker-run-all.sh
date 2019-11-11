#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

LOGFILE="DOCKER-RUN.LOG"

images=$(./docker-build.sh | grep '^\(debian\|fedora\)')

rm -f $LOGFILE

for img in $images; do
    echo "./docker-run.sh $img"
    ./docker-run.sh $img
done
