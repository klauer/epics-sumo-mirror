#!/bin/sh

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

PWD_NICE=`pwd`

echo -e "\n-> Test sumo makeconfig (2)" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB
CONFIG=$ME-CONFIG.tmp
MODULES=$ME-MODULES.tmp

# create config file:
$PYTHON ../bin/sumo --#include $MODULES --arch vxWorks-68040 --arch vxWorks-ppc603 --alias MCAN:MULTICAN --alias ALARM:BSPDEP_ALARM --builddb BUILDS.DB --buildtag-stem MYAPP --db DEPS.DB --extra "extra line" --makeopts "-sj" --progress --readonly --scandb SCAN --supportdir /supports --verbose makeconfig $CONFIG

echo "generated config file:"
cat $CONFIG

# create modules file:
$PYTHON ../bin/sumo -m 'MCAN:R2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:R3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0' makeconfig $MODULES

echo "generated modules file:"
cat $MODULES

echo "read modulespecs from config and modules file:"
# now check if they can be scanned:
$PYTHON ../bin/sumo build -c $CONFIG try --db $DEPS --dump-modules

