#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new-0.tst"
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

echo -e "\n-> Test sumo build state (query)" >&2

SUPPORTDIR=tmp-sumo-build-new-0

echo "state of AUTO-001:"
$SUMO build --builddir $SUPPORTDIR state AUTO-001
echo
echo "state of AUTO-002:"
$SUMO build --builddir $SUPPORTDIR state AUTO-002
