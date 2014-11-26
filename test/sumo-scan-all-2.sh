#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-build-new.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-scan all with buildtree" >&2

TESTDIR=tmp-sumo-build-new-2

$SUMO_SCAN --ignore-changes 'configure/RELEASE' -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -p -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all --buildtag MYAPP-001 | sed -e "s#`pwd -P`##;s#$PWD_NICE##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"

