#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-db distribution." >&2

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB distribution stable ALARM BSPDEP_CPUBOARDINIT BSPDEP_TIMER VXSTATS CSM EK MCAN ASYN SOFT GENSUB SEQ | sed -e "s/,$/, /g"



