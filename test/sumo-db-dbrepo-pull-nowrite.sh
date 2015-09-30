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

echo -e "\n-> Test sumo db cloneversion with --dbrepo (mode 'pull', readonly)." >&2

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

chmod a-w local-darcs local-hg local-git local-svn local-cvs

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

echo "sumo db list ALARM without --dbrepo:"
echo "------------------------------------"
$SUMO db --dbdir local-darcs list ALARM
$SUMO db --dbdir local-hg list ALARM
$SUMO db --dbdir local-git list ALARM
$SUMO db --dbdir local-svn list ALARM
$SUMO db --dbdir local-cvs list ALARM
echo
echo "sumo db list ALARM with --dbrepo (fetch changes from central repo)"
echo "------------------------------------------------------------------"
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode pull list ALARM 2>&1
$SUMO db --dbdir local-hg --dbrepo "hg central-hg" --dbrepomode pull list ALARM 2>&1 
$SUMO db --dbdir local-git --dbrepo "git central-git" --dbrepomode pull list ALARM 2>&1
$SUMO db --dbdir local-svn --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn" --dbrepomode pull list ALARM 2>&1
$SUMO db --dbdir local-cvs --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" --dbrepomode pull list ALARM 2>&1
