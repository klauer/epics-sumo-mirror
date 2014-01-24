#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build apprelease" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS apprelease 001 MCAN | sed -e "s#`pwd -P`##"

