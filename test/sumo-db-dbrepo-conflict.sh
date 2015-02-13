#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst sumo-db-cloneversion-dbrepo.tst"
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

REPOSRC="tmp-sumo-db-dbrepo-create/central"
CHG_REPO="tmp-sumo-db-cloneversion-dbrepo"
EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db --dbrepo with a pull-conflict." >&2

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

# now add patches to the central repositories:
(cd ../$CHG_REPO/central-darcs && darcs push -a ../../$EXAMPLEDIR/central-darcs > /dev/null)
(cd ../$CHG_REPO/central-hg && hg push -q ../../$EXAMPLEDIR/central-hg)
git clone -q ../$CHG_REPO/central-git delme-git 
git -C delme-git config push.default simple
git -C delme-git push -q ../central-git

#echo "sumo db show ALARM without --dbrepo:"
#echo "----------------------------------------"
#$SUMO db --db local-darcs/DEPS.DB show ALARM
#$SUMO db --db local-hg/DEPS.DB show ALARM
#$SUMO db --db local-git/DEPS.DB show ALARM
#echo
#echo "sumo db show ALARM with --dbrepo (fetch changes from central repo)"
#echo "----------------------------------------"

# provoke a pull conflict by applying the changes that were done in the central
# repo again. We do use --dbrepomode get in these calls to avoid that sumo does
# a 'pull' before applying the changes:
$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-hg    --dbrepo "darcs central-hg" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null
$SUMO db --dbdir local-git   --dbrepo "darcs central-git" --dbrepomode get -y cloneversion ALARM R3-7 R3-8-2 >/dev/null

# darcs pull --no-allow-conflicts $?!=0
# hg pull
# hg update --config ui.merge=internal:merge : $?!=0
# git pull : $?!=0

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
