#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-build try" >&2

$PYTHON ../bin/sumo-build --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB --maxstate stable --builddb BUILDS try ALARM:R3-8 BSPDEP_CPUBOARDINIT BSPDEP_TIMER VXSTATS CSM EK MCAN ASYN GENSUB SEQ 





