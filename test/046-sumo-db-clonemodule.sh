#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db cloneversion." >&2

cp samples/IDCP-DEPS.DB $ME-DEPS.tmp

$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp clonemodule ALARM ALARM3-8 R3-8 
$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp clonemodule MCAN MCAN-COPY
cat $ME-DEPS.tmp 

