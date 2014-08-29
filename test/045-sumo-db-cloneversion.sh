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

$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp cloneversion ALARM R3-8 R3-4 darcs '*' R3-4
$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp cloneversion ASYN PATH-4-18 R4-19 darcs 'rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/support/asyn/4-19' R4-19
cat $ME-DEPS.tmp 

