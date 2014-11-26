#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-scan-all.tst"
        echo
        exit
fi

# This program uses the scan file hat was created for test sumo-scan-all.

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

EXAMPLEDIR=tmp-$ME

echo -e "\n-> Test sumo db convert." >&2

if [ ! -d $EXAMPLEDIR ]; then
    echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
    mkdir $EXAMPLEDIR
fi

# if PWD_NICE and PWD_REAL happen to be the same, option "-P" of sumo db is not
# really tested here:
PWD_NICE=`pwd`
PWD_REAL=`pwd -P`

# the following is a trick to remove the "no dependency info" messages
# from standard error and leave standard out untouched:

# sumo db complains if these files already exist:
rm -f $EXAMPLEDIR/DEPS.DB $EXAMPLEDIR/SCAN.DB

set +o posix

$PYTHON ../bin/sumo db convert tmp-sumo-scan-all/SCAN -D "r\"^$PWD_REAL\",r\"$PWD_NICE\"" -U "r\"^$PWD_REAL\",r\"$PWD_NICE\"" --db $EXAMPLEDIR/DEPS.DB --scandb $EXAMPLEDIR/SCAN.DB 2> >(grep -v 'no dependency info' 1>&2) 

echo "DB file:"
cat $EXAMPLEDIR/DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
echo
echo "SCANDB file:"
cat $EXAMPLEDIR/SCAN.DB


