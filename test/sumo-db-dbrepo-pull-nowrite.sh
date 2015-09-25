#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst sumo-db-cloneversion-dbrepo.tst"
        echo
        exit
fi

source settings.sh

REPOSRC="tmp-sumo-db-dbrepo-create/central"
REPOSRC_SVN="tmp-sumo-db-dbrepo-create/central-svn"
CHG_REPO="tmp-sumo-db-cloneversion-dbrepo"

echo -e "\n-> Test sumo db cloneversion with --dbrepo (mode 'pull', readonly)." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null
darcs get -q ../$REPOSRC central-darcs
hg clone -q ../$REPOSRC central-hg
git clone --bare -q ../$REPOSRC central-git
# do just a file copy from the original subversion repo:
cp -a ../$REPOSRC_SVN central-svn

# clone the original repositories
darcs clone -q central-darcs local-darcs
hg clone -q central-hg local-hg
git clone -q central-git local-git
svn checkout -q file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk local-svn
svn checkout -q file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk local-svn-patched
svn checkout -q file://$PWD_NICE/$CHG_REPO/central-svn/trunk local-svn-chg

chmod a-w local-darcs local-hg local-git local-svn

# now add patches to the central repositories:
(cd ../$CHG_REPO/central-darcs && darcs push -a ../../$EXAMPLEDIR/central-darcs > /dev/null)
(cd ../$CHG_REPO/central-hg && hg push -q ../../$EXAMPLEDIR/central-hg)
git clone -q ../$CHG_REPO/central-git delme-git 
git -C delme-git config push.default simple
git -C delme-git push -q ../central-git
(cd local-svn-chg && svn diff -c `svnversion`) > local-svn-patched/PATCH
svn log local-svn-chg -r head | tail -n 2 | head -n 1 > local-svn-patched/PATCH-LOG
(cd local-svn-patched >/dev/null && patch -s -p0 < PATCH)
svn commit -q local-svn-patched -F local-svn-patched/PATCH-LOG

echo "sumo db list ALARM without --dbrepo:"
echo "------------------------------------"
$SUMO db --dbdir local-darcs list ALARM
$SUMO db --dbdir local-hg list ALARM
$SUMO db --dbdir local-git list ALARM
$SUMO db --dbdir local-svn list ALARM
echo
echo "sumo db list ALARM with --dbrepo (fetch changes from central repo)"
echo "------------------------------------------------------------------"
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode pull list ALARM 2>&1
$SUMO db --dbdir local-hg --dbrepo "hg central-hg" --dbrepomode pull list ALARM 2>&1 
$SUMO db --dbdir local-git --dbrepo "git central-git" --dbrepomode pull list ALARM 2>&1
$SUMO db --dbdir local-svn --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn" --dbrepomode pull list ALARM 2>&1
