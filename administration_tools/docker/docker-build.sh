#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

source docker.config

LOGFILE="DOCKER-BUILD.LOG"

APPLICATION=sumo

if [ -z "$1" -o "$1" = "-h" ]; then
    me=`basename $0`
    echo "$me : create a docker container"
    echo
    echo "usage: $me DOCKERFILE" 
    echo "where DOCKERFILE is one of the following:"
    ls docker
    exit 1
fi

set -e

DOCKERFILE="$1"

DOCKERIMAGE=hzb/$APPLICATION-builder-$DOCKERFILE

if [ ! -e docker/$DOCKERFILE ]; then
    echo "error, debian version $DEBIANVERSION not supported"
    exit 1
fi

cd docker

echo "---------------------------------------" >> $MYDIR/$LOGFILE
echo "$me $DOCKERFILE" >> $MYDIR/$LOGFILE

$DOCKER build -t $DOCKERIMAGE -f `pwd -P`/$DOCKERFILE `pwd -P` 2>&1 | tee -a $MYDIR/$LOGFILE

