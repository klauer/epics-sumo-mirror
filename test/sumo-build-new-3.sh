#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build new (use remote build dir)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

OTHERDIR=tmp-sumo-build-new

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# use an auto generated build tag:
$SUMO build --dbdir ../$OTHERDIR --localbuilddir . --builddir ../$OTHERDIR -m ':build:MYAPP-001 ALARM:R3-7' --buildtag MYAPP-002 --no-make new 2>&1

echo -e "\ndirectory tree"
echo "> ls $EXAMPLEDIR:"
ls | sort -f -d 
echo
echo "> ls $EXAMPLEDIR/ALARM:"
ls  ALARM | sort -f -d
echo
echo "> ls $EXAMPLEDIR/MCAN:"
ls  MCAN | sort -f -d
echo -e "\ncontent of BUILDS.DB:"
cat BUILDS.DB 
echo -e "\ncontent of Makefile-MYAPP-002"
cat Makefile-MYAPP-002 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

