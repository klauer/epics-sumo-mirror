#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi
PYTHON=$1

echo -e "\n-> Test sumo-build delete" >&2

TESTDIR=tmp-110-sumo-build-new-2
# this directory must exist
MYTESTDIR=tmp-$ME

if [ -e $MYTESTDIR ]; then
    rm -rf $MYTESTDIR
fi

echo -e "\tcopy $TESTDIR to $MYTESTDIR..." >&2

cp -a $TESTDIR $MYTESTDIR

cd $MYTESTDIR > /dev/null

for f in `find . -name RELEASE`; do
    sed -i $f -e "s#$TESTDIR#$MYTESTDIR#g"
done

rm -f *.tmp
rm -f *.bak

echo -e "\ndirectory tree (without darcs)"
find . -name _darcs -prune -o -name '*' | sort

echo -e "\ncontents of BUILDS file:"
cat BUILDS | sed -e "s/,$/, /g"

echo -e "\ndelete build '002'"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS delete 002

echo -e "\ndirectory tree (without darcs)"
find . -name _darcs -prune -o -name '*' | sort

echo -e "\ncontents of BUILDS file:"
cat BUILDS | sed -e "s/,$/, /g"

echo -e "\ndelete build '001'"
$PYTHON ../../bin/sumo-build --db DB --builddb BUILDS delete 001

echo -e "\ndirectory tree (without darcs)"
find . -name _darcs -prune -o -name '*' | sort

echo -e "\ncontents of BUILDS file:"
cat BUILDS | sed -e "s/,$/, /g"

