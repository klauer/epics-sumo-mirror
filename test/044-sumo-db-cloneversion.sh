#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db cloneversion with wrong sourcespec." >&2

cp samples/IDCP-DEPS.DB $ME-DEPS.tmp

# this command is inteded to fail with "invalid sourcespec":
$PYTHON ../bin/sumo-db --db $ME-DEPS.tmp cloneversion ALARM R3-8 R3-4 '*' '*' R3-4 2>&1 || true

