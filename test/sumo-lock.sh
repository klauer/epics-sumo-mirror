#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo lock" >&2

rm -rf $EXAMPLEDIR
echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
mkdir -p $EXAMPLEDIR
touch $EXAMPLEDIR/A

echo "creating a lock"
$SUMO lock $EXAMPLEDIR/A
echo "listing of $EXAMPLEDIR now:"
ls $EXAMPLEDIR
echo "removing the lock"
$SUMO unlock $EXAMPLEDIR/A
echo "listing of $EXAMPLEDIR now:"
ls $EXAMPLEDIR
echo
echo "creating a lock"
$SUMO lock $EXAMPLEDIR/A
echo "try to create the lock again (should fail)"
$SUMO lock $EXAMPLEDIR/A 2>&1 | sed -e 's/\(locked:\).*/\1 simpson@burns.com:12345/'
echo "removing the lock"
$SUMO unlock $EXAMPLEDIR/A
echo "listing of $EXAMPLEDIR now:"
ls $EXAMPLEDIR
echo 
echo "unlock without locking before"
$SUMO unlock $EXAMPLEDIR/A 2>&1

true
