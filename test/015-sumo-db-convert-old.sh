#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db convert-old." >&2

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

set +o posix
$PYTHON ../bin/sumo-db convert-old samples/DB_IDCP_OLD --db $ME-DEPS.tmp --scandb $ME-SCAN.tmp 
echo "DB file:"
cat $ME-DEPS.tmp
echo
echo "SCANDB file:"
cat $ME-SCAN.tmp


