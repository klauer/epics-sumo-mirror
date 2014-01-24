#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build state (query)" >&2

TESTDIR=tmp-test08
# this directory must exist

cd $TESTDIR > /dev/null

$PYTHON ../../bin/sumo-build --builddb BUILDS state 001 
