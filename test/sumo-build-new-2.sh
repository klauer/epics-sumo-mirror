#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build new (use existing tree)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

OTHERDIR=tmp-sumo-build-new

rm -rf $EXAMPLEDIR

cp -a $OTHERDIR $EXAMPLEDIR

cd $EXAMPLEDIR > /dev/null

for f in `find . -name RELEASE`; do
sed -i $f -e "s#$OTHERDIR#$EXAMPLEDIR#g"
done

rm -f *.tmp
rm -f *.bak

# use an auto generated build tag:
$SUMO build --dbdir . --builddir . -m ':build:MYAPP-001 ALARM:R3-7' --buildtag MYAPP-002 new --makeflags '-s' 2>&1 

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

