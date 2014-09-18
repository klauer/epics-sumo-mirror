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

echo -e "\n-> Test sumo-db cloneversion with wrong sourcespec." >&2

cp tmp-020-sumo-db-convert/DEPS.DB $ME-DEPS.tmp

# this command is inteded to fail with "invalid sourcespec":
$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp cloneversion ALARM TAGLESS-3-8 R3-4 '*' '*' R3-4 2>&1 || true

