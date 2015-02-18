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

EXAMPLEDIR=tmp-$ME
DEPSDIR=tmp-sumo-db-convert

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db list with no write access to the directory" >&2

if [ -d $EXAMPLEDIR ]; then
    chmod u+w $EXAMPLEDIR
    rm -rf $EXAMPLEDIR
fi

echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
cp -a $DEPSDIR $EXAMPLEDIR
chmod a-w $EXAMPLEDIR

$SUMO db --dbdir $EXAMPLEDIR list 

