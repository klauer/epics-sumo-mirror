#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build use with incomplete spec" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "\nsumo build use, incomplete with buildtag:"
$SUMO build --dbdir . --builddir . use -t MYAPP-002 MCAN:R2-6-3-gp -o - | sed -e "s#`pwd -P`##"

echo -e "\nsumo build use, incomplete without buildtag:"
$SUMO build --dbdir . --builddir . use MCAN:R2-6-3-gp -o - 2>&1 | sed -e "s#`pwd -P`##"


