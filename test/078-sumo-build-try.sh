#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo-db-convert.tst 076-sumo-build-new-0.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build try" >&2

DEPS=tmp-020-sumo-db-convert/DEPS.DB
BUILDS=076-sumo-build-new-0-BUILD.tmp

echo -e "try with modules missing:\n"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS try ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC 

echo -e "\n----------------------------"
echo -e "\ntry with complete modulelist:\n"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS try BASE ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC MISC_DEBUGMSG SOFT_DEVHWCLIENT

echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist:\n"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:R3-0
