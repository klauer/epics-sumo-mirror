#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build use" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS use -t MYAPP-001 MCAN -o - | sed -e "s#`pwd -P`##"

