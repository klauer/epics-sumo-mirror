#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 080-sumo-build-new.tst 100-sumo-build-state-2.tst"
        echo
        exit
fi
PYTHON=$@

echo -e "\n-> Test sumo-build new (add dependencies to DB on the fly)" >&2

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


    # use an auto generated build tag,
    # use --add-deps to add new dependencies to the DB file on the fly:
    $PYTHON ../../bin/sumo-build --arch vxWorks-ppc603 --maxstate stable --db DB --builddb BUILDS -m ':build:MYAPP-001 ALARM:R3-7 MCAN:R2-6-1' --add-deps --no-make new 1>&2 
else
    echo -e "\t$MYTESTDIR already exists, effectively skipping this test..." 1>&2
    cd $MYTESTDIR > /dev/null
fi


echo -e "\ndirectory tree (without darcs)"
find . | egrep -v '_darcs|\.tmp|\.bak|\.coverage' | sort
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name RELEASE | sort`; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`##"; done
echo -e "\n\ncontent of DB:"
cat DB 
echo -e "\ncontent of BUILDS"
cat BUILDS 
echo -e "\ncontent of Makefile-AUTO-001"
cat Makefile-AUTO-001

