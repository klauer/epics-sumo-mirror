#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build find MCAN" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "sumo-build find MCAN -b:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN | sed -e "s/,$/, /g"

echo -e "\nsumo-build find MCAN BSPDEP_TIMER:R5-1"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN BSPDEP_TIMER:R5-1 | sed -e "s/,$/, /g"


echo -e "\nsumo-build find MCAN ALARM:-R3-4:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN ALARM:-R3-4 | sed -e "s/,$/, /g"


echo -e "\nsumo-build find MCAN ALARM:+R3-5:"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS find MCAN ALARM:+R3-5 | sed -e "s/,$/, /g"


