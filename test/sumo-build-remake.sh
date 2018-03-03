#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build remake" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../$DEPS .

$SUMO --dbdir . --builddir . config make sumo.config

$SUMO -c sumo.config build  --buildtag-stem BASE --no-make new BASE:R3-14-12-2-1 2>&1 
$SUMO -c sumo.config build  --buildtag-stem MYAPP --no-make new BASE:R3-14-12-2-1 ALARM:R3-7 EK:R2-2 BSPDEP_CPUBOARDINIT:R4-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 2>&1 

echo -e "\ncall sumo build remake"
$SUMO -c sumo.config build remake MYAPP-001 --dry-run | sed -e "s#$PWD_NICE##g;s#$PWD_REAL##g"

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | sort -f -d | grep -v '_darcs\|\.hg\(\|ignore\)\|\.svn\|CVSROOT\|\.git\(\|ignore\)\|\.tmp\|\.bak\|\.coverage'
echo -e "\ncontent of BUILDS"
cat BUILDS.DB
echo -e "\ncontent of Makefile-BASE-001"
cat Makefile-BASE-001
echo -e "\ncontent of Makefile-MYAPP-001"
cat Makefile-MYAPP-001

