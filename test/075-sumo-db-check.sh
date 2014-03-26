#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db check" >&2

echo -e "sumo-db --db samples/DB check:"

$PYTHON ../bin/sumo-db --db samples/DB check

echo -e "\nsumo-db --db samples/BUILDS check:"

$PYTHON ../bin/sumo-db --db samples/BUILDS check 2>&1 | tail -n 1


