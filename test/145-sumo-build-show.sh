#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build show" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo-build show 001"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS show 001 | sed -e "s/,$/, /g"

echo -e "\nsumo-build show 002"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS show 002 | sed -e "s/,$/, /g"

