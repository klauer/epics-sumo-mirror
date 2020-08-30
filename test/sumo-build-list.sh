#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build list" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo build list"
$SUMO build --dbdir . --builddir . list

echo
echo -e "sumo build list --sort-build-dependencies-first"
$SUMO build --dbdir . --builddir . list --sort-build-dependencies-first

echo
echo -e "sumo build list --sort-build-dependencies-last"
$SUMO build --dbdir . --builddir . list --sort-build-dependencies-last

