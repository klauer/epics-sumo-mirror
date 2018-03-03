#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build delete --recursive without write permissions" >&2

TESTDIR=tmp-sumo-build-new-2

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

# now intentionally remove write permissions at some place:
chmod 555 CSM

echo -e "\ndirectory tree:"
echo "> ls $EXAMPLEDIR:"
ls | sort -f -d 
echo -e "\nbuild directories:"
find . -name '*+*' | sort -f -d

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB

echo -e "\ndelete build 'MYAPP-001' recursively"
$SUMO build --dbdir . --builddir . delete MYAPP-001 --yes --recursive 2>&1

echo -e "\nbuild directories:"
find . -name '*+*' | sort -f -d

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB


