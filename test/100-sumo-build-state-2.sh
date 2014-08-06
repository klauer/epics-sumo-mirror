#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 080-sumo-build-new.tst"
        echo
        exit
fi


PYTHON=$@

echo -e "\n-> Test sumo-build state (setting)" >&2

TESTDIR=tmp-080-sumo-build-new
# this directory must exist

cd $TESTDIR > /dev/null


echo -e "\nBUILDS before:"
cat BUILDS 

cp DB DB-$ME.tmp
cp BUILDS BUILDS-$ME.tmp
$PYTHON ../../bin/sumo-build --db DB-$ME.tmp --builddb BUILDS-$ME.tmp state MYAPP-001 stable

echo -e "\nBUILDS after:"
cat BUILDS-$ME.tmp 

