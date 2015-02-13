#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db find" >&2

DEPSDIR=tmp-sumo-db-convert

echo -e "find mcan:"
$SUMO db --dbdir $DEPSDIR find mcan | sed -e s#$PWD_NICE##

echo -e "\nfind mcan -b:"
$SUMO db --dbdir $DEPSDIR find mcan -b | sed -e s#$PWD_NICE##

echo -e "\nfind '^A' -b:"
$SUMO db --dbdir $DEPSDIR find '^A' -b | sed -e s#$PWD_NICE##

