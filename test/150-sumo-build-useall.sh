#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo build--new.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo build useall" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "\nsumo-build useall MYAPP-001:"
$PYTHON ../../bin/sumo build --builddb BUILDS.DB --db DEPS.DB useall MYAPP-001 -o - | sed -e "s#`pwd -P`##"

echo -e "\nsumo-build useall MYAPP-002:"
$PYTHON ../../bin/sumo build --builddb BUILDS.DB --db DEPS.DB useall MYAPP-002 -o - | sed -e "s#`pwd -P`##"

