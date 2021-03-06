#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db show" >&2

DEPSDIR=tmp-sumo-db-convert

echo "show details of all ALARM modules:"
$SUMO db --dbdir $DEPSDIR show ALARM | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

echo "show details of MCAN:TAGLESS-2-6-1:"
$SUMO db --dbdir $DEPSDIR show MCAN:TAGLESS-2-6-1 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

echo "show details of BSPDEP_TIMER and BSPDEP_CPUBOARDINIT:"
$SUMO db --dbdir $DEPSDIR show BSPDEP_TIMER BSPDEP_CPUBOARDINIT | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

