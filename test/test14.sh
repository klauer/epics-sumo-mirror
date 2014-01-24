#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-buildtree findtree MCAN" >&2

TESTDIR=tmp-test11

cd $TESTDIR > /dev/null

echo -e "pys-buildtree findtree MCAN -b:"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS findtree MCAN | sed -e "s/,$/, /g"

echo -e "\npys-buildtree findtree MCAN BSPDEP_TIMER:R5-1"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS findtree MCAN BSPDEP_TIMER:R5-1 | sed -e "s/,$/, /g"


echo -e "\npys-buildtree findtree MCAN ALARM:-R3-4:"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS findtree MCAN ALARM:-R3-4 | sed -e "s/,$/, /g"


echo -e "\npys-buildtree findtree MCAN ALARM:+R3-5:"
$PYTHON ../../bin/pys-buildtree --builddb BUILDS findtree MCAN ALARM:+R3-5 | sed -e "s/,$/, /g"


