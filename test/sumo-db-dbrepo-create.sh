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

EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db list with --dbrepo (repo cloning)" >&2

rm -rf $EXAMPLEDIR
echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
mkdir -p $EXAMPLEDIR/central 

OLD_DEPS=tmp-sumo-db-convert/DEPS.DB

cp $OLD_DEPS $EXAMPLEDIR/central
cd $EXAMPLEDIR/central >/dev/null
darcs init -q
darcs add -q DEPS.DB
darcs record -q -a -m 'initial record'

hg init
hg add DEPS.DB
hg commit -m 'initial record'

git init -q
git add DEPS.DB
git commit -a -q -m 'initial record'
cd ..

$SUMO db --dbdir local-darcs --dbrepo 'darcs central' list 
$SUMO db --dbdir local-hg    --dbrepo 'hg central' list 
$SUMO db --dbdir local-git   --dbrepo 'git central' list 
