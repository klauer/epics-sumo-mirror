#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

PWD_NICE=`pwd`

echo -e "\n-> Test sumo makeconfig." >&2

DEPS=tmp-sumo-db-convert/DEPS.DB
CONFIG=$ME-CONFIG.tmp
MODULES=$ME-MODULES.tmp

# create config file:
$SUMO --no-default-config --#preload $MODULES --arch vxWorks-68040 --arch vxWorks-ppc603 --db DEPS.DB --progress --scandb SCAN -D 'r"^/srv/csr/Epics",r"rcsadm@aragon.acc.bessy.de:/opt/Epics"' --verbose makeconfig $CONFIG

echo "generated config file:"
cat $CONFIG

# create modules file:
$SUMO --no-default-config -m 'BASE:R3-14-12-2-1 MCAN:R2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0' makeconfig $MODULES

echo "generated modules file:"
cat $MODULES

echo "read modulespecs from config and modules file:"
# now check if they can be scanned:
$SUMO db --no-default-config -c $CONFIG filter --db $DEPS --dump-modules

