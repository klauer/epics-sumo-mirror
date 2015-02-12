#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`

echo -e "\n-> Test sumo build delete after crash(some seconds nothing will seem to happen)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB
BUILDS="sumo-build-new-0-BUILD.tmp"

TESTDIR=tmp-$ME

if [ -e $TESTDIR ]; then
    rm -rf $TESTDIR
fi

mkdir $TESTDIR
# create an error in DEPS.DB:
cat $DEPS | sed -e 's#repos/base/#repo/mybase#' > $TESTDIR/DEPS.DB

cd $TESTDIR > /dev/null

echo -e "call sumo build new, let the command fail on purpose..."

$SUMO build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --builddir . --buildtag 001 --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-3-gp BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 | tail -n 1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
#echo -e "\ndirectory tree (without darcs)"
#find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort

echo -e "\ncontents of BUILDS.DB:"
cat BUILDS.DB

echo -e "\nnow do sumo build delete 001"

$SUMO --builddir . build delete 001

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
#echo -e "\ndirectory tree now (without darcs)"
#find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort

echo -e "\ncontents of BUILDS.DB now:"
cat BUILDS.DB
