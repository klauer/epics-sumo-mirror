#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build new" >&2

DEPS=tmp-020-sumo-db-convert/DEPS.DB

TESTDIR=tmp-$ME

if [ ! -d $TESTDIR ]; then
    mkdir $TESTDIR
    cp $DEPS $TESTDIR/DEPS.DB

    cd $TESTDIR > /dev/null

    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --builddb BUILDS.DB --buildtag-stem BASE --no-make new BASE:R3-14-12-2-1 1>&2 
    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --builddb BUILDS.DB state BASE-001 stable 1>&2 
    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --builddb BUILDS.DB --buildtag-stem MYAPP --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-3-gp BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0 1>&2 
    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --builddb BUILDS.DB state MYAPP-001 testing 1>&2 
else
    echo -e "\t$TESTDIR already exists, effectively skipping this test..." 1>&2
    cd $TESTDIR > /dev/null
fi

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name RELEASE | grep -v 'makeBase\(App\|Ext\)' | sort`; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`#mysumo#"; done
echo -e "\ncontent of BUILDS"
cat BUILDS.DB
echo -e "\ncontent of Makefile-BASE-001"
cat Makefile-BASE-001
echo -e "\ncontent of Makefile-MYAPP-001"
cat Makefile-MYAPP-001


