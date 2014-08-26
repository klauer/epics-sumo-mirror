#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build cleanup (for some seconds nothing will seem to happen)" >&2

TESTDIR=tmp-$ME

if [ -e $TESTDIR ]; then
    rm -rf $TESTDIR
fi

mkdir $TESTDIR
cat samples/DEPS.DB | sed -e 's#R[0-9\.]\+/base#epicsbase#' > $TESTDIR/DEPS.DB
cp samples/IDCP.CONFIG $TESTDIR

cd $TESTDIR > /dev/null

echo -e "call sumo-build new, let the command fail on purpose..."

$PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB -c IDCP.CONFIG --builddb BUILDS --buildtag 001 --no-make new 2>&1 | tail -n 1

echo -e "\ndirectory tree (without darcs)"
find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort

echo -e "\ncontents of cleanup file:"
cat cleanup-001 

echo -e "\nnow do sumo-build cleanup 001"

$PYTHON ../../bin/sumo-build cleanup 001

echo -e "\ndirectory tree now (without darcs)"
find . -name _darcs -prune -o -name '*' | grep -v '.coverage' | sort




