#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build find MCAN" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo-build find MCAN -b:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN 

echo -e "\nsumo-build find MCAN BSPDEP_TIMER:R5-1"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN BSPDEP_TIMER:R5-1 


echo -e "\nsumo-build find MCAN ALARM:-R3-7:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN ALARM:-R3-7 


echo -e "\nsumo-build find MCAN ALARM:+R3-8:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN ALARM:+R3-8 


