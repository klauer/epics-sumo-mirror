#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo-scan: checkout many modules and scan the directory tree." >&2
echo -e "\tIf run for the first time this may take a while..." >&2

if [ ! -d $EXAMPLEDIR ]; then
    echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
    mkdir $EXAMPLEDIR
fi

#echo $SUMO_SCAN -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
#$SUMO_SCAN -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
$SUMO_SCAN -d "$SUPPORTDIR/base $SUPPORTDIR/support" -g "$SUPPORTDIR/support $SUPPORTDIR" -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all > $EXAMPLEDIR/SCAN

cat $EXAMPLEDIR/SCAN | sed -e "s#`pwd -P`##;s#`pwd`##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
