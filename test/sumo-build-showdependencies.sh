#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build showdependencies" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../$DEPS .

$SUMO --dbdir . --builddir . config make sumo.config

echo "Create the builds..."

# create a first build "BASE" with the base
$SUMO -c sumo.config build  --buildtag 04-BASE --no-make new BASE:R3-14-12-2-1 2>&1 
$SUMO -c sumo.config build  state 04-BASE testing 2>&1 

# now create a build "BSPDEP_TIMER" that depends on the base:
$SUMO -c sumo.config build  --buildtag 03-BSPDEP_TIMER --no-make new BASE:R3-14-12-2-1 BSPDEP_TIMER:R6-2 2>&1 
$SUMO -c sumo.config build  state 03-BSPDEP_TIMER testing 2>&1 

# now create a build "MISC_DBC" that depends on the base:
$SUMO -c sumo.config build  --buildtag 02-MISC_DBC --no-make new BASE:R3-14-12-2-1 MISC_DBC:PATH-3-0 2>&1 
$SUMO -c sumo.config build  state 02-MISC_DBC testing 2>&1 

# now create a build "ALARM" that depends on the base, BSPDEP_TIMER and MISC_DBC
$SUMO -c sumo.config build  --buildtag ALARM --no-make new BASE:R3-14-12-2-1 BSPDEP_TIMER:R6-2 MISC_DBC:PATH-3-0 ALARM:R3-7 2>&1 
$SUMO -c sumo.config build  state ALARM testing 2>&1 

echo
echo "dependencies:"

for tag in 04-BASE 03-BSPDEP_TIMER 02-MISC_DBC ALARM ""; do
    echo -e "sumo build showdependencies $tag"
    $SUMO -c sumo.config build showdependencies $tag
done

