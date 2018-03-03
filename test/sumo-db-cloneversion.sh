#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db cloneversion with wrong sourcespec." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

# this command is inteded to fail with "invalid sourcespec":
$SUMO db --dbdir . cloneversion ALARM R3-8-modified R3-4 '*' '*' R3-4 2>&1 | grep -v "'lockfile' not found"|| true

