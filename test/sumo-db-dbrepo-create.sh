#!/bin/sh

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

$PYTHON ../../bin/sumo db --db "local-darcs/DEPS.DB" --dbrepo 'darcs central' list 
$PYTHON ../../bin/sumo db --db "local-hg/DEPS.DB" --dbrepo 'hg central' list 
$PYTHON ../../bin/sumo db --db "local-git/DEPS.DB" --dbrepo 'git central' list 
