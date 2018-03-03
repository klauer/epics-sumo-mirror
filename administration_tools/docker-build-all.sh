#!/bin/bash

images=$(./docker-build.sh | grep '^\(debian\|fedora\)')

for img in $images; do
    ./docker-build.sh $img
done
