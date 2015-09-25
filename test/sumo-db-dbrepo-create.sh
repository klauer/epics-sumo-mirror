#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

source settings.sh

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

cd .. >/dev/null && mkdir central-svn && svnadmin create --fs-type fsfs central-svn
mkdir tmp-svn && cd tmp-svn >/dev/null
mkdir trunk branches tags
cp ../central/DEPS.DB trunk
svn import -q file://$PWD_NICE/$EXAMPLEDIR/central-svn -m "initial commit"
cd .. >/dev/null && rm -rf tmp-svn

$SUMO db --dbdir local-darcs --dbrepo 'darcs central' list 
$SUMO db --dbdir local-hg    --dbrepo 'hg central' list 
$SUMO db --dbdir local-git   --dbrepo 'git central' list 
$SUMO db --dbdir local-svn   --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk" list 
