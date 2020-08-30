#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build showdependents" >&2

TESTDIR=tmp-sumo-build-showdependencies

cd $TESTDIR > /dev/null

for tag in 04-BASE 03-BSPDEP_TIMER 02-MISC_DBC ALARM ""; do
    echo -e "sumo build showdependents $tag"
    $SUMO -c sumo.config build showdependents $tag
done

echo -e "\nsumo build showdependents --sort-build-dependencies-first:"
$SUMO -c sumo.config build showdependents --sort-build-dependencies-first

echo -e "\nsumo build showdependents --sort-build-dependencies-last:"
$SUMO -c sumo.config build showdependents --sort-build-dependencies-last
