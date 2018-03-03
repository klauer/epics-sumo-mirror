#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

ssh -t goetzpf,epics-sumo@shell.sourceforge.net create
