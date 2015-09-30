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
REPOSRC_CVS="tmp-sumo-db-dbrepo-create/central-cvs"
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
# do just a file copy from the original cvs repo:
cp -a ../$REPOSRC_CVS central-cvs

# clone the original repositories
darcs clone -q central-darcs local-darcs
hg clone -q central-hg local-hg
git clone -q central-git local-git
svn checkout -q file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk local-svn
cvs -d $PWD_NICE/$EXAMPLEDIR/central-cvs checkout sumo-database >/dev/null 2>&1 && mv sumo-database local-cvs

# now add patches to the central repositories:
(cd ../$CHG_REPO/central-darcs && darcs push -a ../../$EXAMPLEDIR/central-darcs > /dev/null)
(cd ../$CHG_REPO/central-hg && hg push -q ../../$EXAMPLEDIR/central-hg)
git clone -q ../$CHG_REPO/central-git delme-git 
git -C delme-git config push.default simple
git -C delme-git push -q ../central-git

# adding a patch to subversion is a bit more complicated, we use the files
# PATCH and LOGMESSAGE that were created in another test:
svn checkout -q file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk local-svn-patched
(cd local-svn-patched >/dev/null && patch -s -p1 < ../../$CHG_REPO/extra/PATCH)
svn commit -q local-svn-patched -F ../$CHG_REPO/extra/LOGMESSAGE
rm -rf local-svn-patched

# adding a patch to cvs is also a bit more complicated, we use the files
# PATCH and LOGMESSAGE that were created in another test:
cvs -d $PWD_NICE/$EXAMPLEDIR/central-cvs checkout sumo-database >/dev/null 2>&1 && mv sumo-database local-cvs-patched
(cd local-cvs-patched >/dev/null && patch -s -p1 < ../../$CHG_REPO/extra/PATCH)
(cd local-cvs-patched >/dev/null && cvs commit -F ../../$CHG_REPO/extra/LOGMESSAGE >/dev/null 2>&1)
rm -rf local-cvs-patched

# provoke a pull conflict by applying the changes that were done in the central
# repo again. We do use --dbrepomode get in these calls to avoid that sumo does
# a 'pull' before applying the changes:
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-hg    --dbrepo "darcs central-hg" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-git   --dbrepo "darcs central-git" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
# Note: with subversion and cvs, "sumo cloneversion" would immediately lead to
# a conflict, since subversion always contacts the central repo. So we do "sumo
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
echo
echo "Conflict in cvs repo:"
echo "---------------------"
$SUMO db --dbdir local-cvs   --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 2>&1 1>/dev/null
$SUMO db -y --logmsg "local changes" --dbdir local-cvs --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" --dbrepomode pull show ALARM 2>&1 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##" 
