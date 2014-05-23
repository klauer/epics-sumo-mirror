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

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp dependency-add ALARM:R3-8 CSM:R4.3 testing
cat DB_IDCP-$ME.tmp | sed -e "s/,$/, /g"

