#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-buildtree state (query)" >&2

TESTDIR=tmp-test08
# this directory must exist

cd $TESTDIR > /dev/null

$PYTHON ../../bin/pys-buildtree --builddb BUILDS state 001 
