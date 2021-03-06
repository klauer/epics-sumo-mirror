#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build find MCAN" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo build find MCAN:"
$SUMO build --dbdir . --builddir . find MCAN 

echo -e "\nsumo-build find MCAN ALARM:R3-7"
$SUMO build --dbdir . --builddir . find MCAN ALARM:R3-7

echo -e "\nsumo-build find MCAN ALARM:-R3-7:"
$SUMO build --dbdir . --builddir . find MCAN ALARM:-R3-7 

echo -e "\nsumo-build find MCAN ALARM:+R3-8:"
$SUMO build --dbdir . --builddir . find MCAN ALARM:+R3-8 

echo -e "\nsumo build find MCAN -b:"
$SUMO build --dbdir . --builddir . find MCAN -b

echo -e "\nsumo build find MCAN -b --sort-build-dependencies-first:"
$SUMO build --dbdir . --builddir . find MCAN -b --sort-build-dependencies-first 

echo -e "\nsumo build find MCAN -b --sort-build-dependencies-last:"
$SUMO build --dbdir . --builddir . find MCAN -b --sort-build-dependencies-last 

