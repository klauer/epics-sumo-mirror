#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo db-convert.tst 110-sumo build--new.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo build delete" >&2

DEPS=tmp-020-sumo-db-convert/DEPS.DB

TESTDIR=tmp-110-sumo-build-new-2
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

echo -e "\ndirectory tree:"
echo "> ls $MYTESTDIR:"
ls  
echo -e "\nbuild directories:"
find . -name '*+*'

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB

echo -e "\ndelete build 'MYAPP-002'"
$PYTHON ../../bin/sumo build --db DB --builddb BUILDS.DB delete MYAPP-002

echo -e "\nbuild directories:"
find . -name '*+*'

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB

echo -e "\ndelete build 'MYAPP-001'"
$PYTHON ../../bin/sumo build --db DB --builddb BUILDS.DB delete MYAPP-001

echo -e "\nbuild directories:"
find . -name '*+*'

echo -e "\ncontents of BUILDS file:"
cat BUILDS.DB 

