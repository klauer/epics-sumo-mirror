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

echo -e "\n-> Test sumo build new (use existing tree)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

OTHERDIR=tmp-sumo-build-new
TESTDIR=tmp-$ME

rm -rf $TESTDIR

echo -e "\tcopy $OTHERDIR to $MYTESTDIR..." >&2

cp -a $OTHERDIR $TESTDIR

cd $TESTDIR > /dev/null

for f in `find . -name RELEASE`; do
sed -i $f -e "s#$OTHERDIR#$TESTDIR#g"
done

rm -f *.tmp
rm -f *.bak

# use an auto generated build tag:
$SUMO build --dbdir . --builddir . -m ':build:MYAPP-001 ALARM:R3-7' --buildtag MYAPP-002 --no-make new 1>&2 

echo -e "\ndirectory tree"
echo "> ls $TESTDIR:"
ls  
echo
echo "> ls $TESTDIR/ALARM:"
ls  ALARM
echo
echo "> ls $TESTDIR/MCAN:"
ls  MCAN
echo -e "\ncontent of BUILDS.DB:"
cat BUILDS.DB 
echo -e "\ncontent of Makefile-MYAPP-002"
cat Makefile-MYAPP-002

