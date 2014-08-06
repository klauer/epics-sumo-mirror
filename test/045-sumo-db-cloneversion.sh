#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db cloneversion." >&2

cp samples/DB_IDCP DB_IDCP-$ME.tmp

$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp cloneversion ALARM R3-8 R3-4 darcs '*' R3-4
cat DB_IDCP-$ME.tmp 

