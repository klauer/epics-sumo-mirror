#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

DEPSDIR=tmp-sumo-db-convert

echo -e "\n-> Test sumo db list with no write access to the directory" >&2

if [ -d $EXAMPLEDIR ]; then
    chmod u+w $EXAMPLEDIR
    rm -rf $EXAMPLEDIR
fi

cp -a $DEPSDIR $EXAMPLEDIR
chmod a-w $EXAMPLEDIR

$SUMO db --dbdir $EXAMPLEDIR list 

