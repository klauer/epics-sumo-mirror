#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo build--new.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-scan all with buildtree" >&2

TESTDIR=tmp-110-sumo-build-new-2

$PYTHON ../bin/sumo-scan --ignore-changes 'configure/RELEASE' -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -p -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all --buildtag MYAPP-001 | sed -e "s#`pwd -P`##;s#$PWD_NICE##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"

