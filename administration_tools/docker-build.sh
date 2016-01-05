#!/bin/bash

if [ -z "$1" -o "$1" = "-h" ]; then
    me=`basename $0`
    echo "$me : create a docker container"
    echo
    echo "usage: $me DOCKERFILE" 
    echo "where DOCKERFILE is one of the following:"
    ls docker
    exit 1
fi

DOCKERFILE="$1"

DOCKERIMAGE=hzb/sumo-builder-$DOCKERFILE

if [ ! -e docker/$DOCKERFILE ]; then
    echo "error, debian version $DEBIANVERSION not supported"
    exit 1
fi

cd docker && docker build -t $DOCKERIMAGE -f `pwd -P`/$DOCKERFILE `pwd -P`

