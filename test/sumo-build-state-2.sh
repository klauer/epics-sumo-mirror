#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new-0.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build state (setting)" >&2

if [ ! -d $EXAMPLEDIR ]; then
    mkdir $EXAMPLEDIR
fi
cp tmp-sumo-build-new-0/BUILDS.DB $EXAMPLEDIR

echo -e "\nBUILDS before:"
cat $EXAMPLEDIR/BUILDS.DB

echo -e "\nNow change state of AUTO-002 to stable"
$SUMO build --builddir $EXAMPLEDIR state AUTO-002 stable

echo -e "\nBUILDS now:"
cat $EXAMPLEDIR/BUILDS.DB

echo -e "\nNow change state of AUTO-001 to disabled, changes AUTO-002,too"
$SUMO build --builddir $EXAMPLEDIR -y state AUTO-001 disabled

echo -e "\nBUILDS now:"
cat $EXAMPLEDIR/BUILDS.DB

