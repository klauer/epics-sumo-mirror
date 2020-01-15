#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

# This program uses the scan file hat was created for test sumo-scan-all.

echo -e "\n-> Test sumo db modconvert." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

set +o posix

$SUMO db modconvert tmp-sumo-scan-all/SCAN SOFT_DEVHWCLIENT SEQ -D "r\"^$PWD_REAL\",''" -D "r\"$PWD_NICE\",''" -U "r\"^$PWD_REAL\",''" -U "r\"$PWD_NICE\",''" 

