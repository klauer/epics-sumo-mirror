#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build list" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo-build list"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS list

