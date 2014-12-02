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

echo -e "\n-> Test sumo build state (setting)" >&2

TESTDIR=tmp-$ME

if [ ! -d $TESTDIR ]; then
    mkdir $TESTDIR
fi
cp tmp-sumo-build-new-0/BUILDS.DB $TESTDIR

echo -e "\nBUILDS before:"
cat $TESTDIR/BUILDS.DB

$SUMO build --builddir $TESTDIR state AUTO-002 stable

echo -e "\nBUILDS after:"
cat $TESTDIR/BUILDS.DB

