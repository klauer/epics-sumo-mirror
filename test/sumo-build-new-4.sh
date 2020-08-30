#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build new when a build already exists" >&2

OTHERDIR=tmp-sumo-build-new

rm -rf $EXAMPLEDIR

cp -a $OTHERDIR $EXAMPLEDIR

cd $EXAMPLEDIR > /dev/null

# save original BUILDS.DB file:
cp BUILDS.DB BUILDS.DB.orig

$SUMO -c sumo.config build  --buildtag-stem MYAPP --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified EK:R2-2 MCAN:R2-6-3-gp BSPDEP_CPUBOARDINIT:R4-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified CSM:TAR-4-1 MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 

echo "Changes in BUILDS.DB:"
diff BUILDS.DB.orig BUILDS.DB || true
