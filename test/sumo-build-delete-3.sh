#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst sumo-build-new.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build delete --recursive" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

TESTDIR=tmp-sumo-build-new-2
EXAMPLEDIR=tmp-$ME

if [ -e $EXAMPLEDIR ]; then
    rm -rf $EXAMPLEDIR
fi

cp -a $TESTDIR $EXAMPLEDIR

cd $EXAMPLEDIR > /dev/null

for f in `find . -name RELEASE`; do
    sed -i $f -e "s#$TESTDIR#$EXAMPLEDIR#g"
done

rm -f *.tmp
rm -f *.bak

echo -e "\ndirectory tree:"
echo "> ls $EXAMPLEDIR:"
ls | sort -f -d 
echo -e "\nbuild directories:"
find . -name '*+*' | sort -f -d

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB

echo -e "\ndelete build 'MYAPP-001' recursively"
$SUMO build --dbdir . --builddir . delete MYAPP-001 --recursive

echo -e "\nbuild directories:"
find . -name '*+*' | sort -f -d

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB
