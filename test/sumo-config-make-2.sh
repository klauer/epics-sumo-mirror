#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo config make (2)" >&2

DEPSDIR=tmp-sumo-db-convert
CONFIG=$ME-CONFIG.tmp
MODULES=$ME-MODULES.tmp

# create config file:
$SUMO --no-default-config --#preload $MODULES --alias MCAN:MULTICAN --alias ALARM:BSPDEP_ALARM --buildtag-stem MYAPP --dbdir . --extra "extra line" --makeflags "-sj" --progress --readonly --scandb SCAN --builddir /supports --verbose config make $CONFIG

echo "generated config file:"
cat $CONFIG

# create modules file:
$SUMO --no-default-config -m 'MCAN:TAGLESS-2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0' config make $MODULES

echo "generated modules file:"
cat $MODULES

echo "read modulespecs from config and modules file:"
# now check if they can be scanned:
$SUMO build --no-default-config -c $CONFIG try --dbdir $DEPSDIR --dump-modules

