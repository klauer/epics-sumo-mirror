#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 076-sumo-build-new-0.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build state (setting)" >&2

BUILDS=$ME-BUILD.tmp
cp 076-sumo-build-new-0-BUILD.tmp $BUILDS

echo -e "\nBUILDS before:"
cat $BUILDS 

$PYTHON ../bin/sumo-build --builddb $BUILDS state AUTO-002 stable

echo -e "\nBUILDS after:"
cat $BUILDS

