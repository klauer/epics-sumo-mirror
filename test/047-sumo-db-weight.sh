#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db weight" >&2

cp samples/IDCP-DEPS.DB $ME-DEPS.tmp

$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp -- weight -1 MCAN MISC_DBC
$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp weight 1 ALARM
cat $ME-DEPS.tmp 

