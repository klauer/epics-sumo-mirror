#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db cloneversion." >&2

cp samples/DB_IDCP DB_IDCP-$ME.tmp

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp clonemodule ALARM ALARM3-8 R3-8 
$PYTHON ../bin/sumo-db --db DB_IDCP-$ME.tmp clonemodule MCAN MCAN-COPY
cat DB_IDCP-$ME.tmp | sed -e "s/,$/, /g"

