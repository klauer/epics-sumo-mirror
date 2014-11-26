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

PWD_NICE=`pwd`

echo -e "\n-> Test sumo build state (query)" >&2

BUILDS=sumo-build-new-0-BUILD.tmp

echo "state of AUTO-001:"
$PYTHON ../bin/sumo build --builddb $BUILDS state AUTO-001
echo
echo "state of AUTO-002:"
$PYTHON ../bin/sumo build --builddb $BUILDS state AUTO-002
