#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db convert." >&2

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

set +o posix
$PYTHON ../bin/sumo-db convert stable samples/SCAN -P 'r"^/srv/csr/Epics",r"rcsadm@aragon.acc.bessy.de:/opt/Epics"' 2> >(grep -v 'no dependency info' 1>&2) 

