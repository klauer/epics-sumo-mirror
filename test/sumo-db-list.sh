#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo db list" >&2

DEPSDIR=tmp-sumo-db-convert

echo "list without arguments:"
$SUMO db --dbdir $DEPSDIR list 

echo "list with '.':"
$SUMO db --dbdir $DEPSDIR list .

echo "list ALARM:"
$SUMO db --dbdir $DEPSDIR list ALARM

echo "list BSPDEP_TIMER:R6-2:"
$SUMO db --dbdir $DEPSDIR list BSPDEP_TIMER:R6-2

