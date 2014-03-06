#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build useall" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "\nsumo-build useall 001:"
$PYTHON ../../bin/sumo-build --builddb BUILDS --db DB useall 001 | sed -e "s#`pwd -P`##"

echo -e "\nsumo-build useall 002:"
$PYTHON ../../bin/sumo-build --builddb BUILDS --db DB useall 002 | sed -e "s#`pwd -P`##"

