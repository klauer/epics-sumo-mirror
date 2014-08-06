#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db replaceversion." >&2

cp samples/DB_IDCP DB_IDCP-$ME.tmp

$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp dependency-add ALARM:R3-8 CSM:R4.3 testing
cat DB_IDCP-$ME.tmp 

