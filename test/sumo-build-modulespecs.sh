#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst sumo-db-makeconfig.tst sumo-build-new-0.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build modulespecs" >&2

DEPSDIR=tmp-sumo-db-convert
CONFIG=sumo-config-make-CONFIG.tmp
MODULES=sumo-config-make-MODULES.tmp

SUPPORTDIR=tmp-sumo-build-new-0

echo "Take modulespecs from modules file"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --dump-modules try :load:$MODULES
echo
echo "Take modulespecs from build file:"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --dump-modules try :build:AUTO-001
echo
echo "The same but remove ALARM:R3-7"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --dump-modules try :build:AUTO-001 :rm:ALARM:R3-7
echo
echo "The same but change ALARM:R3-7 to ALARM:R3-8"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --dump-modules try :build:AUTO-001 ALARM:R3-8
echo
echo "The same but remove all and add ALARM:R3-8"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --dump-modules try :build:AUTO-001 :clear ALARM:R3-8

