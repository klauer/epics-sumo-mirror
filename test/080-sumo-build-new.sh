#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build new" >&2

TESTDIR=tmp-$ME

if [ ! -d $TESTDIR ]; then
    mkdir $TESTDIR
    cp samples/DEPS.DB $TESTDIR
    cp samples/IDCP.CONFIG $TESTDIR

    cd $TESTDIR > /dev/null

    $PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB -c IDCP.CONFIG --builddb BUILDS --buildtag-stem MYAPP --no-make new 1>&2 
else
    echo -e "\t$TESTDIR already exists, effectively skipping this test..." 1>&2
    cd $TESTDIR > /dev/null
fi



echo -e "\ndirectory tree (without darcs)"
find . | egrep -v '_darcs|\.tmp|\.bak|\.coverage'
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name RELEASE | sort`; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`##"; done
echo -e "\n\ncontent of DB:"
cat DEPS.DB 
echo -e "\ncontent of BUILDS"
cat BUILDS 
echo -e "\ncontent of Makefile-MYAPP-001"
cat Makefile-MYAPP-001

