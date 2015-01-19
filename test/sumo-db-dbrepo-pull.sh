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

echo -e "\n-> Test sumo db cloneversion with --dbrepo (mode 'pull')." >&2

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

echo "sumo db show ALARM without --dbrepo:"
echo "------------------------------------"
$SUMO db --db local-darcs/DEPS.DB show ALARM
$SUMO db --db local-hg/DEPS.DB show ALARM
$SUMO db --db local-git/DEPS.DB show ALARM
echo
echo "sumo db show ALARM with --dbrepo (fetch changes from central repo)"
echo "------------------------------------------------------------------"
$SUMO db --db local-darcs/DEPS.DB --dbrepo "darcs central-darcs" --dbrepomode pull show ALARM
$SUMO db --db local-hg/DEPS.DB --dbrepo "hg central-hg" --dbrepomode pull show ALARM
$SUMO db --db local-git/DEPS.DB --dbrepo "git central-git" --dbrepomode pull show ALARM
