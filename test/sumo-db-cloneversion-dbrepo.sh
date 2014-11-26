#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst"
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
EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db cloneversion with --dbrepo (repo commit)" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null
darcs get -q ../$REPOSRC central-darcs
hg clone -q ../$REPOSRC central-hg
git clone --bare -q ../$REPOSRC central-git

$SUMO db --db local-darcs/DEPS.DB --dbrepo "darcs central-darcs" -y cloneversion ALARM R3-7 R3-8-1
$SUMO db --db local-hg/DEPS.DB --dbrepo "hg central-hg" -y cloneversion ALARM R3-7 R3-8-1
$SUMO db --db local-git/DEPS.DB --dbrepo "git central-git" -y cloneversion ALARM R3-7 R3-8-1

DDATE="Mon Jan 01 01:01:01 2014 +0100"
DUSR="Homer.Simpson@burns.com"
DHSH="ffffffffffff"
echo
echo "==========================================="
echo "Test of darcs:"
echo
echo "Logs of local repository:"
echo "-------------------------------------------"
(cd local-darcs >/dev/null && darcs changes | sed -e "s/^.*\<[0-9:]\{8\}\>.*/$DDATE  $DUSR/")
echo
echo "Logs of central repository:"
echo "-------------------------------------------"
(cd central-darcs >/dev/null && darcs changes | sed -e "s/^.*\<[0-9:]\{8\}\>.*/$DDATE  $DUSR/")
echo
echo "==========================================="
echo "Test of mercurial:"
echo
echo "Logs of local repository:"
echo "-------------------------------------------"
hg -R local-hg log | sed -e "s/^\(date: \+\).*/\1$DDATE/;s/^\(user: \+\).*/\1$DUSR/;s/^\(changeset: \+[0-9]\+:\).*/\1$DHSH/"
echo
echo "Logs of central repository:"
echo "-------------------------------------------"
hg -R central-hg log | sed -e "s/^\(date: \+\).*/\1$DDATE/;s/^\(user: \+\).*/\1$DUSR/;s/^\(changeset: \+[0-9]\+:\).*/\1$DHSH/"
echo
echo "==========================================="
echo "Test of git:"
echo
echo "Logs of local repository:"
echo "-------------------------------------------"
git -C local-git log | sed -e "s/^\(Date: \+\).*/\1$DDATE/;s/^\(Author: \+\).*/\1$DUSR/;s/^\(commit \).*/\1$DHSH/"
echo
echo "Logs of central repository:"
echo "-------------------------------------------"
git -C central-git log | sed -e "s/^\(Date: \+\).*/\1$DDATE/;s/^\(Author: \+\).*/\1$DUSR/;s/^\(commit \).*/\1$DHSH/"
