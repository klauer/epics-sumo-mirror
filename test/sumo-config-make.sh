#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo config make." >&2

DEPSDIR=tmp-sumo-db-convert
CONFIG=$ME-CONFIG.tmp
MODULES=$ME-MODULES.tmp

# create config file:
$SUMO --no-default-config --#preload $MODULES --dbdir . --progress --scandb SCAN -D 'r"^/srv/csr/Epics",r"rcsadm@aragon.acc.bessy.de:/opt/Epics"' --verbose config make $CONFIG

echo "generated config file:"
cat $CONFIG

# create modules file:
$SUMO --no-default-config -m 'BASE:R3-14-12-2-1 MCAN:TAGLESS-2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0' config make $MODULES

echo "generated modules file:"
cat $MODULES

echo "read modulespecs from config and modules file:"
# now check if they can be scanned:
$SUMO db --no-default-config -c $CONFIG show --dbdir $DEPSDIR --dump-modules

