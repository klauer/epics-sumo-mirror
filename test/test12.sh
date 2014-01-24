#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-build partialdb" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS partialdb 001 | sed -e "s/,$/, /g"


