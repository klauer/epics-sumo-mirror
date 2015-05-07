#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst sumo-build-new.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build new (use existing tree)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

OTHERDIR=tmp-sumo-build-new

rm -rf $EXAMPLEDIR

echo -e "\tcopy $OTHERDIR to $MYTESTDIR..." >&2

cp -a $OTHERDIR $EXAMPLEDIR

cd $EXAMPLEDIR > /dev/null

for f in `find . -name RELEASE`; do
sed -i $f -e "s#$OTHERDIR#$EXAMPLEDIR#g"
done

rm -f *.tmp
rm -f *.bak

# use an auto generated build tag:
$SUMO build --dbdir . --builddir . -m ':build:MYAPP-001 ALARM:R3-7' --buildtag MYAPP-002 new 1>&2 

echo -e "\ndirectory tree"
echo "> ls $EXAMPLEDIR:"
ls  
echo
echo "> ls $EXAMPLEDIR/ALARM:"
ls  ALARM
echo
echo "> ls $EXAMPLEDIR/MCAN:"
ls  MCAN
echo -e "\ncontent of BUILDS.DB:"
cat BUILDS.DB 
echo -e "\ncontent of Makefile-MYAPP-002"
cat Makefile-MYAPP-002

