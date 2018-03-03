#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db weight" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

$SUMO db --dbdir . -- weight -1 MCAN:TAGLESS-2-6-1 MISC_DBC
$SUMO db --dbdir . weight 1 ALARM
cat DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
