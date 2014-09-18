#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo-db-convert.tst 074-sumo-db-makeconfig.tst 076-sumo-build-new-0.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo-build modulespecs" >&2

DEPS=tmp-020-sumo-db-convert/DEPS.DB
BUILDS=076-sumo-build-new-0-BUILD.tmp
CONFIG=074-sumo-db-makeconfig-CONFIG.tmp
MODULES=074-sumo-db-makeconfig-MODULES.tmp

echo "Take modulespecs from modules file"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS --dump-modules try :load:$MODULES
echo
echo "Take modulespecs from build file:"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS --dump-modules try :build:AUTO-001
echo
echo "The same but remove ALARM:R3-7"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS --dump-modules try :build:AUTO-001 :rm:ALARM:R3-7
echo
echo "The same but change ALARM:R3-7 to ALARM:R3-8"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS --dump-modules try :build:AUTO-001 ALARM:R3-8
echo
echo "The same but remove all and add ALARM:R3-8"
$PYTHON ../bin/sumo-build --db $DEPS --builddb $BUILDS --dump-modules try :build:AUTO-001 :clear ALARM:R3-8

