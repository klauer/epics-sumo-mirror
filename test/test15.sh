#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-buildtree fullapprelease" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "\npys-buildtree fullapprelease 001:"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS fullapprelease 001 | sed -e "s#`pwd -P`##"

echo -e "\npys-buildtree fullapprelease 002:"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS fullapprelease 002 | sed -e "s#`pwd -P`##"

