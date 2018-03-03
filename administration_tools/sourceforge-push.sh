#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

hg push ssh://goetzpf@hg.code.sf.net/p/epics-sumo/mercurial
