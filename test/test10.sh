#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-buildtree state (setting)" >&2

TESTDIR=tmp-test08
# this directory must exist

cd $TESTDIR > /dev/null

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.

echo -e "\nBUILDS before:"
cat BUILDS | sed -e "s/,$/, /g"

cp DB DB-10.tmp
cp BUILDS BUILDS-10.tmp
$PYTHON ../../bin/pys-buildtree --db DB-10.tmp --builddb BUILDS-10.tmp state 001 stable

echo -e "\nBUILDS after:"
cat BUILDS-10.tmp | sed -e "s/,$/, /g"

