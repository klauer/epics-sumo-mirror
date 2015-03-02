#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build new --no-checkout." >&2

DEPSDIR=tmp-sumo-db-convert

EXAMPLEDIR=tmp-$ME
if [ ! -d $EXAMPLEDIR ]; then
    mkdir $EXAMPLEDIR
fi
rm -f $EXAMPLEDIR/BUILDS.DB

$SUMO build --dbdir $DEPSDIR --builddir $EXAMPLEDIR new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:PATH-3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 
$SUMO build --dbdir $DEPSDIR --builddir $EXAMPLEDIR state AUTO-001 stable
$SUMO build --dbdir $DEPSDIR --builddir $EXAMPLEDIR new --no-checkout BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-8-modified BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:PATH-3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 

echo "BUILD file:"
cat $EXAMPLEDIR/BUILDS.DB
