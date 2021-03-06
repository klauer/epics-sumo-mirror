#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

DEPSDIR=tmp-sumo-db-convert

echo -e "\n-> Test sumo db check" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# create an error by putting a BUILD.DB file to DEPS.DB:
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

$SUMO db --dbdir ../$DEPSDIR check

echo -e "\nsumo db --dbdir $EXAMPLEDIR check:"

$SUMO db --dbdir . check 2>&1 
true
