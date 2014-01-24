#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-scan all with buildtree" >&2

TESTDIR=tmp-test11

$PYTHON ../bin/sumo-scan -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -p all --buildtag 001 | sed -e "s#`pwd -P`##;s/,$/, /g"

