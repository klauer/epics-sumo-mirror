#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new.tst"
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

echo -e "\n-> Test sumo build use with exact spec" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

$SUMO build --dbdir . --builddir . use -t MYAPP-002 MCAN:R2-6-3-gp ALARM:R3-7 -o - | sed -e "s#`pwd -P`##"


