#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

LOGFILE="DOCKER-BUILD.LOG"

cd "$MYDIR"

images=$(./docker-build.sh | grep '^\(debian\|fedora\)')

rm -f $LOGFILE

for img in $images; do
    ./docker-build.sh $img 
done
