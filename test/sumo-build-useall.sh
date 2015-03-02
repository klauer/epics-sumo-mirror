#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build useall" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

echo -e "\nsumo-build useall MYAPP-001:"
$SUMO build --builddir . --dbdir . useall MYAPP-001 -o - | sed -e "s#`pwd -P`##"

echo -e "\nsumo-build useall MYAPP-002:"
$SUMO build --builddir . --dbdir . useall MYAPP-002 -o - | sed -e "s#`pwd -P`##"

