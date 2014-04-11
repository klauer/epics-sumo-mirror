#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 080-sumo-build-new.tst 040-sumo-db-replaceversion.tst 100-sumo-build-state-2.tst"
        echo
        exit
fi
PYTHON=$1

echo -e "\n-> Test sumo-build new (use existing tree)" >&2

TESTDIR=tmp-080-sumo-build-new
# this directory must exist
MYTESTDIR=tmp-$ME

if [ ! -d $MYTESTDIR ]; then
    echo -e "\tcopy $TESTDIR to $MYTESTDIR..." >&2

    cp -a $TESTDIR $MYTESTDIR

    cd $MYTESTDIR > /dev/null

    for f in `find . -name RELEASE`; do
        sed -i $f -e "s#$TESTDIR#$MYTESTDIR#g"
    done

    # copy the DB and BUILDS file where everything is marked "stable" (see also
    # test10.sh):
    cp DB-100-sumo-build-state-2.tmp DB
    cp BUILDS-100-sumo-build-state-2.tmp BUILDS

    rm -f *.tmp
    rm -f *.bak

    # sed is used to add spaces after each "," at the end of the line. The old JSON
    # library for python 2.5 doesn't do this.

    # use an auto generated build tag:
    $PYTHON ../../bin/sumo-build --arch vxWorks-ppc603 --db DB -P ../DB_IDCP-040-sumo-db-replaceversion.tmp --builddb BUILDS --no-make new 1>&2 
else
    echo -e "\t$MYTESTDIR already exists, effectively skipping this test..." 1>&2
    cd $MYTESTDIR > /dev/null
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
echo -e "\ncontent of Makefile-AUTO-001"
cat Makefile-AUTO-001

