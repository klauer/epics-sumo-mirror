#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db list with --dbrepo (repo cloning)" >&2

rm -rf $EXAMPLEDIR
mkdir -p $EXAMPLEDIR/central 

OLD_DEPS=tmp-sumo-db-convert/DEPS.DB

# create a directory "central" that contains the central repository for all
# three distributed version controls systems, git, mercurial and darcs:
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

cd .. >/dev/null

# The central version control systems cannot co-exist with the others, so they
# get a directory of their own.

# Create the central subversion repository:
mkdir central-svn && svnadmin create --fs-type fsfs central-svn
mkdir tmp-svn && cd tmp-svn >/dev/null
mkdir trunk branches tags
cp ../central/DEPS.DB trunk
svn import -q file://$PWD_NICE/$EXAMPLEDIR/central-svn -m "initial commit"
cd .. >/dev/null && rm -rf tmp-svn

# Create the central cvs repository:
mkdir central-cvs && cvs -d `pwd`/central-cvs init 
CVSROOT="`pwd`/central-cvs"
export CVSROOT
mkdir x && cd x>/dev/null && cvs import -m 'initial version' sumo-database me initial-version >/dev/null
cd .. >/dev/null && rm -rf x
cvs checkout sumo-database 2>/dev/null
cd sumo-database >/dev/null
cp ../central/DEPS.DB .
cvs add DEPS.DB 2>/dev/null
cvs -q commit -m 'DEPS.DB was added to the repository.' >/dev/null
cd .. >/dev/null && rm -rf sumo-database

# now test if the initial checkout works:
$SUMO db --dbdir local-darcs --dbrepo 'darcs central' list 
$SUMO db --dbdir local-hg    --dbrepo 'hg central' list 
$SUMO db --dbdir local-git   --dbrepo 'git central' list 
$SUMO db --dbdir local-svn   --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk" list 
$SUMO db --dbdir local-cvs   --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" list 
