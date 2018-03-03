#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build use with incomplete spec" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "\nsumo build use, incomplete with buildtag:"
$SUMO build --dbdir . --builddir . use -t MYAPP-002 MCAN:R2-6-3-gp -o - | sed -e "s#`pwd -P`##"

echo -e "\nsumo build use, incomplete without buildtag but unique:"
$SUMO build --dbdir . --builddir . use MCAN:R2-6-3-gp ALARM:R3-7 -o - 2>&1 | sed -e "s#`pwd -P`##"

echo -e "\nsumo build use, incomplete without buildtag, not unique:"
$SUMO build --dbdir . --builddir . use MCAN:R2-6-3-gp -o - 2>&1 | sed -e "s#`pwd -P`##"


