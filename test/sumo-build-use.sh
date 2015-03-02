#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build use" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

$SUMO build --dbdir . --builddir . use -t MYAPP-002 MCAN -o - | sed -e "s#`pwd -P`##"


