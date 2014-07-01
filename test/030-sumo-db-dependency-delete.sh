#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db replaceversion." >&2

cp samples/DB_IDCP DB_IDCP-$ME.tmp

$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp dependency-delete ALARM:R3-8 BSPDEP_TIMER:R6-2 
cat DB_IDCP-$ME.tmp 

