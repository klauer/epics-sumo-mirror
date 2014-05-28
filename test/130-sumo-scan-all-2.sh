#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 110-sumo-build-new-2.tst"
        echo
        exit
fi

PYTHON=$1

# needed since sumo-scan call EPICS make:
EPICS_HOST_ARCH=`scripts/EpicsHostArch.pl`
export EPICS_HOST_ARCH

echo -e "\n-> Test sumo-scan all with buildtree" >&2

TESTDIR=tmp-110-sumo-build-new-2

$PYTHON ../bin/sumo-scan -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -p -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all --buildtag MYAPP-001 | sed -e "s#`pwd -P`##;s/,$/, /g"

