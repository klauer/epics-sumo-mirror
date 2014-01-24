#!/bin/bash

PYTHON=$1

echo -e "\n-> Test pys-db convert." >&2

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
set +o posix
$PYTHON ../bin/pys-db convert stable samples/SCAN 2> >(grep -v 'no dependency info' 1>&2) | sed -e "s/,$/, /g"

