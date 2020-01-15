#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo-scan: checkout many modules and scan directory tree." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR

#echo $SUMO_SCAN -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
#$SUMO_SCAN -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
$SUMO_SCAN -d "$SUPPORTDIR/base $SUPPORTDIR/support" -g "$SUPPORTDIR/support $SUPPORTDIR" -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all > $EXAMPLEDIR/SCAN

cat $EXAMPLEDIR/SCAN | sed -e "s#`pwd -P`##;s#`pwd`##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
