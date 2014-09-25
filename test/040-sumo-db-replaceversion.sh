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
PWD_REAL=`pwd -P`

echo -e "\n-> Test sumo-db replaceversion." >&2

cp tmp-020-sumo-db-convert/DEPS.DB $ME-DEPS.tmp

$PYTHON ../bin/sumo-db -y --db $ME-DEPS.tmp replaceversion ALARM R3-8-modified R3-4 darcs '*' R3-4 | sed -e s#$PWD_NICE##
echo "DB file:"
cat $ME-DEPS.tmp | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"



