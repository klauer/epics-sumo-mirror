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
DEPSDIR=tmp-sumo-db-convert

EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db check" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cat > DEPS.DB <<HEE
{
    "MYAPP-001": {
        "modules": {
            "ALARM": "R3-8",
            "ASYN": "4-18-bessy1",
            "BASE": "TAGLESS-3-14-12-2-1",
            "BSPDEP_CPUBOARDINIT": "R4-1",
            "BSPDEP_TIMER": "R6-2",
            "BSPDEP_VMETAS": "R2-0",
            "CSM": "R4-3",
            "EK": "R2-2",
            "GENSUB": "R1-6-1",
            "MCAN": "TAGLESS-2-6-3-test",
            "MISC_DBC": "R3-0",
            "MISC_DEBUGMSG": "R3-0",
            "SEQ": "TAGLESS-2-1-12",
            "SOFT_DEVHWCLIENT": "R3-0",
            "VXSTATS": "R3-0"
        },
        "state": "unstable"
    }
}
HEE

echo -e "sumo db --dbdir tmp-sumo-db-convert samples check:"

$SUMO db --dbdir $DEPSDIR check

echo -e "\nsumo db --dbdir $EXAMPLEDIR check:"

$SUMO db --dbdir . check 2>&1 
true
