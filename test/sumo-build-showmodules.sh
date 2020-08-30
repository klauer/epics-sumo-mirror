#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build showmodules" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "sumo build showmodules MYAPP-001:"
$SUMO build --dbdir . --builddir . showmodules MYAPP-001

echo -e "\nsumo build showmodules MYAPP-001 --lines:"
$SUMO build --dbdir . --builddir . showmodules MYAPP-001 --lines

echo -e "\nsumo build showmodules MYAPP-001 -b --lines:"
$SUMO build --dbdir . --builddir . showmodules MYAPP-001 -b --lines

echo -e "\nsumo build showmodules:"
$SUMO build --dbdir . --builddir . showmodules

echo -e "\nsumo build showmodules -b:"
$SUMO build --dbdir . --builddir . showmodules -b

echo -e "\nsumo build showmodules -b --lines:"
$SUMO build --dbdir . --builddir . showmodules -b --lines

echo -e "\nsumo build showmodules -b --sort-build-dependencies-last:"
$SUMO build --dbdir . --builddir . showmodules --sort-build-dependencies-last

