#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build delete after crash(some seconds nothing will seem to happen)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

if [ -e $EXAMPLEDIR ]; then
    rm -rf $EXAMPLEDIR
fi

mkdir $EXAMPLEDIR
# create an error in DEPS.DB:
cat $DEPS | sed -e 's#repos/base/#repo/mybase/#' > $EXAMPLEDIR/DEPS.DB

cd $EXAMPLEDIR > /dev/null

echo -e "call sumo build new, let the command fail on purpose..."

$SUMO build --dbdir . --builddir . --buildtag 001 --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-3-gp BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 | sed -e "s#$PWD_REAL##g;s#$PWD_NICE##g" | sed -e 's/^darcs failed: *//' | sed -e '/^ *$/d;/^HINT:/d'

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | sort -f -d | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
#echo -e "\ndirectory tree (without darcs)"
#find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort -f -d

echo -e "\ncontents of BUILDS.DB:"
cat BUILDS.DB

echo -e "\nnow do sumo build delete 001"

$SUMO --builddir . build delete 001

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | sort -f -d | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
#echo -e "\ndirectory tree now (without darcs)"
#find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort -f -d

echo -e "\ncontents of BUILDS.DB now:"
cat BUILDS.DB
