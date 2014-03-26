#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi
PYTHON=$1

echo -e "\n-> Test sumo-build partialdb" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS partialdb 001 | sed -e "s/,$/, /g"


