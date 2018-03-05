#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR/.."

DESTHOST=goetzpf@frs.sourceforge.net
DESTPATH=/home/frs/project/epics-sumo
#scp dist/*.tar.gz $DESTHOST:$DESTPATH
#scp dist/*.zip $DESTHOST:$DESTPATH
scp -r dist/* $DESTHOST:$DESTPATH
scp README.rst $DESTHOST:$DESTPATH
