#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build fullapprelease" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "\nsumo-build fullapprelease 001:"
$PYTHON ../../bin/sumo-build --builddb BUILDS fullapprelease 001 | sed -e "s#`pwd -P`##"

echo -e "\nsumo-build fullapprelease 002:"
$PYTHON ../../bin/sumo-build --builddb BUILDS fullapprelease 002 | sed -e "s#`pwd -P`##"

