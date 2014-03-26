#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db convert." >&2

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
set +o posix
$PYTHON ../bin/sumo-db convert stable samples/SCAN -P 'r"^/srv/csr/Epics",r"rcsadm@aragon.acc.bessy.de:/opt/Epics"' 2> >(grep -v 'no dependency info' 1>&2) | sed -e "s/,$/, /g"

