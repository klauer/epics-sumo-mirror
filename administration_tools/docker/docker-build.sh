#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")
SCRIPT=$(basename $ME)

cd "$MYDIR"

source docker.config

if [ -z "$1" -o "$1" = "-h" ]; then
    echo "$SCRIPT : create a docker container"
    echo
    echo "usage: $SCRIPT DOCKERFILE" 
    echo "where DOCKERFILE is one of the following:"
    ls $DOCKERFILEDIR
    exit 1
fi

set -e

DOCKERFILE="$1"

DOCKERIMAGE=$(imagename $DOCKERFILE)

if $DOCKER images | grep -q $DOCKERIMAGE; then
    echo "image $DOCKERIMAGE already exists" >&2
    exit 0
fi

if [ ! -e $DOCKERFILEDIR/$DOCKERFILE ]; then
    echo "error, debian version $DEBIANVERSION not supported"
    exit 1
fi

cd $DOCKERFILEDIR

echo "---------------------------------------" >> $MYDIR/$BUILD_LOGFILE
echo "$me $DOCKERFILE" >> $MYDIR/$BUILD_LOGFILE

$DOCKER build -t $DOCKERIMAGE -f $(pwd -P)/$DOCKERFILE $(pwd -P) 2>&1 | tee -a $MYDIR/$BUILD_LOGFILE

