#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build use with exact spec" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

$SUMO build --dbdir . --builddir . use -t MYAPP-002 MCAN:R2-6-3-gp ALARM:R3-7 -o - | sed -e "s#`pwd -P`##"


