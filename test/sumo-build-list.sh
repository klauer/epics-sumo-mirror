#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build list" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo build list"
$SUMO build --dbdir . --builddir . list

echo -e "\nsumo build list --all-builds"
$SUMO build --dbdir . --builddir . list --all-builds

echo -e "\nsumo build list --sort-build-dependencies-first --all-builds"
$SUMO build --dbdir . --builddir . list --sort-build-dependencies-first --all-builds

echo -e "\nsumo build list --sort-build-dependencies-last --all-builds"
$SUMO build --dbdir . --builddir . list --sort-build-dependencies-last --all-builds

