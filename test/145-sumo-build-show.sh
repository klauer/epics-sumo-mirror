#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build show" >&2

TESTDIR=tmp-110-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo-build show MYAPP-001"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS show MYAPP-001 

echo -e "\nsumo-build show AUTO-001"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS show AUTO-001 

