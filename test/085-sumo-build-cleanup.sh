#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build cleanup (for some seconds nothing will seem to happen)" >&2

TESTDIR=tmp-$ME

if [ -e $TESTDIR ]; then
    rm -rf $TESTDIR
fi

mkdir $TESTDIR
cp samples/DB $TESTDIR
cat samples/DB_IDCP | sed -e 's#epics/base#epicsbase#' > $TESTDIR/DB_IDCP

cd $TESTDIR > /dev/null

echo -e "call sumo-build new, let the command fail on purpose..."

$PYTHON ../../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db DB -P DB_IDCP --builddb BUILDS new 001 2>&1 | tail -n 1

echo -e "\ndirectory tree (without darcs)"
find . -name _darcs -prune -o -name '*' | sort

echo -e "\ncontents of cleanup file:"
cat cleanup-001 | sed -e "s/,$/, /g"

echo -e "\nnow do sumo-build cleanup 001"

$PYTHON ../../bin/sumo-build cleanup 001

echo -e "\ndirectory tree now (without darcs)"
find . -name _darcs -prune -o -name '*' | sort



