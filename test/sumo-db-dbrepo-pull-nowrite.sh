#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst sumo-db-cloneversion-dbrepo.tst"
        echo
        exit
fi

source settings.sh

REPOSRC="tmp-sumo-db-dbrepo-create/central"
CHG_REPO="tmp-sumo-db-cloneversion-dbrepo"

echo -e "\n-> Test sumo db cloneversion with --dbrepo (mode 'pull', readonly)." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null
darcs get -q ../$REPOSRC central-darcs
hg clone -q ../$REPOSRC central-hg
git clone --bare -q ../$REPOSRC central-git

# clone the original repositories
darcs clone -q central-darcs local-darcs
hg clone -q central-hg local-hg
git clone -q central-git local-git

chmod a-w local-darcs local-hg local-git

# now add patches to the central repositories:
(cd ../$CHG_REPO/central-darcs && darcs push -a ../../$EXAMPLEDIR/central-darcs > /dev/null)
(cd ../$CHG_REPO/central-hg && hg push -q ../../$EXAMPLEDIR/central-hg)
git clone -q ../$CHG_REPO/central-git delme-git 
git -C delme-git config push.default simple
git -C delme-git push -q ../central-git

echo "sumo db show ALARM without --dbrepo:"
echo "------------------------------------"
$SUMO db --dbdir local-darcs show ALARM
$SUMO db --dbdir local-hg show ALARM
$SUMO db --dbdir local-git show ALARM
echo
echo "sumo db show ALARM with --dbrepo (fetch changes from central repo)"
echo "------------------------------------------------------------------"
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode pull show ALARM 2>&1
$SUMO db --dbdir local-hg --dbrepo "hg central-hg" --dbrepomode pull show ALARM 2>&1 
$SUMO db --dbdir local-git --dbrepo "git central-git" --dbrepomode pull show ALARM 2>&1
