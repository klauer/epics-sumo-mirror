#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst"
        echo
        exit
fi

source settings.sh

REPOSRC="tmp-sumo-db-dbrepo-create/central"

echo -e "\n-> Test sumo db cloneversion with --dbrepo (repo commit, mode 'get')" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null
darcs get -q ../$REPOSRC central-darcs
hg clone -q ../$REPOSRC central-hg
git clone --bare -q ../$REPOSRC central-git

$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-hg    --dbrepo "hg central-hg" -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-git   --dbrepo "git central-git" -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"

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
