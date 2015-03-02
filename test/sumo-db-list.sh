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

$SUMO db --dbdir $DEPSDIR list 
