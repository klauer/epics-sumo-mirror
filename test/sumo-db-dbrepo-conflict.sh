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

echo -e "\n-> Test sumo db --dbrepo with a pull-conflict." >&2

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

# provoke a pull conflict by applying the changes that were done in the central
# repo again. We do use --dbrepomode get in these calls to avoid that sumo does
# a 'pull' before applying the changes:
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-hg    --dbrepo "darcs central-hg" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-git   --dbrepo "darcs central-git" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
# Note: with subversion, "sumo cloneversion" would immediately lead to a
# conflict, since subversion always contacts the central repo. So we do "sumo
# cloneversion" further below.

echo "Conflict in darcs repo:"
echo "-----------------------"
$SUMO db -y --logmsg "local changes" --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode pull show ALARM 2>&1 || true
echo
echo "Conflict in mercurial repo:"
echo "---------------------------"
$SUMO db -y --logmsg "local changes" --dbdir local-hg --dbrepo "hg central-hg" --dbrepomode pull show ALARM 2>&1 | sed -e 's/\(not updating:\).*/\1/;/(merge or update/d'
echo
echo "Conflict in git repo:"
echo "---------------------"
$SUMO db -y --logmsg "local changes" --dbdir local-git --dbrepo "git central-git" --dbrepomode pull show ALARM 2>&1 || true
echo
echo "Conflict in subversion repo:"
echo "---------------------"
$SUMO db --dbdir local-svn   --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 2>&1 1>/dev/null
$SUMO db -y --logmsg "local changes" --dbdir local-svn --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn" --dbrepomode pull show ALARM 2>&1 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s/: E[0-9]\+//" 
