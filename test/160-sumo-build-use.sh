#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build--new.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build use" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

$PYTHON ../../bin/sumo-build --db DEPS.DB --builddb BUILDS.DB use -t MYAPP-002 MCAN -o - | sed -e "s#`pwd -P`##"


