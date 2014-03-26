#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build useall" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "\nsumo-build useall 001:"
$PYTHON ../../bin/sumo-build --builddb BUILDS --db DB useall 001 | sed -e "s#`pwd -P`##"

echo -e "\nsumo-build useall 002:"
$PYTHON ../../bin/sumo-build --builddb BUILDS --db DB useall 002 | sed -e "s#`pwd -P`##"

