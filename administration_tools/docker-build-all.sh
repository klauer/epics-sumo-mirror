#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

images=$(./docker-build.sh | grep '^\(debian\|fedora\)')

for img in $images; do
    ./docker-build.sh $img
done
