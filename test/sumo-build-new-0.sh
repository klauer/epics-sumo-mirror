#!/bin/sh

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

echo -e "\n-> Test sumo build new --no-checkout." >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

TESTDIR=tmp-$ME
if [ ! -d $TESTDIR ]; then
    mkdir $TESTDIR
fi
rm -f $TESTDIR/BUILDS.DB

$SUMO build --db $DEPS --supportdir $TESTDIR new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:PATH-3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0 
$SUMO build --db $DEPS --supportdir $TESTDIR state AUTO-001 stable
$SUMO build --db $DEPS --supportdir $TESTDIR new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-8-modified BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:PATH-3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0 

echo "BUILD file:"
cat $TESTDIR/BUILDS.DB
