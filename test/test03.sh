#!/bin/sh

PYTHON=$1

echo -e "\n-> Test pys-db distribution." >&2

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/pys-db --db samples/DB distribution stable ALARM BSPDEP_CPUBOARDINIT BSPDEP_TIMER VXSTATS CSM EK MCAN ASYN SOFT GENSUB SEQ | sed -e "s/,$/, /g"


