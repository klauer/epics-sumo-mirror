#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

if [ -d .hg/patches ]; then
    if [ $(hg qapplied | wc -l) != 0 ]; then 
        echo "error, mq patches are applied, hg push aborted"
        exit 1
    fi
fi

hg push ssh://goetzpf@bitbucket.org/goetzpf/epics-sumo
