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

echo -e "\n-> Test sumo-build show" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo-build show MYAPP-001"
$PYTHON ../../bin/sumo-build --db DEPS.DB --builddb BUILDS.DB show MYAPP-001 

echo -e "\nsumo-build show MYAPP-002"
$PYTHON ../../bin/sumo-build --db DEPS.DB --builddb BUILDS.DB show MYAPP-002


