#!/bin/bash

images=$(./docker-build.sh | grep '^\(debian\|fedora\)')

for img in $images; do
    ./docker-run.sh $img
done
