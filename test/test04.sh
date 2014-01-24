#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-db replaceversion." >&2

cp samples/DB_IDCP DB_IDCP-04.tmp

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/pys-db --db DB_IDCP-04.tmp --savedb replaceversion ALARM R3-5 R3-4 
cat DB_IDCP-04.tmp | sed -e "s/,$/, /g"
