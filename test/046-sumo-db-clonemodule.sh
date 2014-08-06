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

$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp clonemodule ALARM ALARM3-8 R3-8 
$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp clonemodule MCAN MCAN-COPY
cat DB_IDCP-$ME.tmp 

