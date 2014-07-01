#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db weight" >&2

cp samples/DB_IDCP DB_IDCP-$ME.tmp

$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp -- weight -1 MCAN MISC_DBC
$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp weight 1 ALARM
cat DB_IDCP-$ME.tmp 

