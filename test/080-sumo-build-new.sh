#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build new" >&2

TESTDIR=tmp-$ME

if [ ! -d $TESTDIR ]; then
    mkdir $TESTDIR
    cp samples/DB $TESTDIR
    cp samples/DB_IDCP $TESTDIR

    cd $TESTDIR > /dev/null

    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DB -P DB_IDCP --builddb BUILDS new 001 1>&2 
else
    echo -e "\t$TESTDIR already exists, effectively skipping this test..." 1>&2
    cd $TESTDIR > /dev/null
fi


# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.

echo -e "\ndirectory tree (without darcs)"
find . | egrep -v '_darcs|\.tmp|\.bak'
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name RELEASE | sort`; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`##"; done
echo -e "\n\ncontent of DB:"
cat DB | sed -e "s/,$/, /g"
echo -e "\ncontent of BUILDS"
cat BUILDS | sed -e "s/,$/, /g"
echo -e "\ncontent of Makefile-001"
cat Makefile-001

