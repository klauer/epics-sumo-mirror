#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-scan all with buildtree" >&2

TESTDIR=tmp-test11

$PYTHON ../bin/pys-scan -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -p all --buildtag 001 | sed -e "s#`pwd -P`##;s/,$/, /g"

