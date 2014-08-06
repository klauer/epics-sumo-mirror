#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 080-sumo-build-new.tst"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build state (query)" >&2

TESTDIR=tmp-080-sumo-build-new
# this directory must exist

cd $TESTDIR > /dev/null

$PYTHON ../../bin/sumo-build --builddb BUILDS state MYAPP-001 
