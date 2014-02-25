#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build findtree MCAN" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "sumo-build findtree MCAN -b:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS findtree MCAN | sed -e "s/,$/, /g"

echo -e "\nsumo-build findtree MCAN BSPDEP_TIMER:R5-1"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS findtree MCAN BSPDEP_TIMER:R5-1 | sed -e "s/,$/, /g"


echo -e "\nsumo-build findtree MCAN ALARM:-R3-4:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS findtree MCAN ALARM:-R3-4 | sed -e "s/,$/, /g"


echo -e "\nsumo-build findtree MCAN ALARM:+R3-5:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS findtree MCAN ALARM:+R3-5 | sed -e "s/,$/, /g"


