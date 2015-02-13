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

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db cloneversion with wrong sourcespec." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

# this command is inteded to fail with "invalid sourcespec":
$SUMO db --dbdir . cloneversion ALARM R3-8-modified R3-4 '*' '*' R3-4 2>&1 | grep -v "'lockfile' not found"|| true

