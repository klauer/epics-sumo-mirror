#!/bin/sh

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

PWD_NICE=`pwd`

echo -e "\n-> Test sumo build find MCAN" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo build find MCAN -b:"
$PYTHON ../../bin/sumo build --db DEPS.DB --builddb BUILDS.DB find MCAN 

echo -e "\nsumo-build find MCAN ALARM:R3-7"
$PYTHON ../../bin/sumo build --db DEPS.DB --builddb BUILDS.DB find MCAN ALARM:R3-7

echo -e "\nsumo-build find MCAN ALARM:-R3-7:"
$PYTHON ../../bin/sumo build --db DEPS.DB --builddb BUILDS.DB find MCAN ALARM:-R3-7 

echo -e "\nsumo-build find MCAN ALARM:+R3-8:"
$PYTHON ../../bin/sumo build --db DEPS.DB --builddb BUILDS.DB find MCAN ALARM:+R3-8 


