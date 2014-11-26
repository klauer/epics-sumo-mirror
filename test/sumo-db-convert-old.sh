#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

echo -e "\n-> Test sumo db convert-old." >&2

set +o posix
$SUMO db convert-old data/samples/DB_IDCP_OLD --db $ME-DEPS.tmp --scandb $ME-SCAN.tmp 
echo "DB file:"
cat $ME-DEPS.tmp
echo
echo "SCANDB file:"
cat $ME-SCAN.tmp


