#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst sumo-build-new.tst"
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

echo -e "\n-> Test sumo build new (use remote build dir)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

TESTDIR=tmp-sumo-build-new
MYTESTDIR=tmp-$ME

if [ ! -d $MYTESTDIR ]; then
    mkdir $MYTESTDIR
    cd $MYTESTDIR > /dev/null

    # use an auto generated build tag:
    $SUMO build --dbdir ../$TESTDIR --localbuilddir . --builddir ../$TESTDIR -m ':build:MYAPP-001 ALARM:R3-7' --buildtag MYAPP-002 --no-make new 1>&2 
else
    echo -e "\t$MYTESTDIR already exists, effectively skipping this test..." 1>&2
    cd $MYTESTDIR > /dev/null
fi

echo -e "\ndirectory tree"
echo "> ls $MYTESTDIR:"
ls  
echo
echo "> ls $MYTESTDIR/ALARM:"
ls  ALARM
echo
echo "> ls $MYTESTDIR/MCAN:"
ls  MCAN
echo -e "\ncontent of BUILDS.DB:"
cat BUILDS.DB 
echo -e "\ncontent of Makefile-MYAPP-002"
cat Makefile-MYAPP-002

