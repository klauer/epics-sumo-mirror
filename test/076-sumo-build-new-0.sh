#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build new --no-checkout." >&2

DEPS=tmp-020-sumo-db-convert/DEPS.DB
BUILD=$ME-BUILD.tmp

$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILD new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0 
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILD state AUTO-001 stable
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILD new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:TAGLESS-3-8 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0 

echo "BUILD file:"
cat $BUILD
