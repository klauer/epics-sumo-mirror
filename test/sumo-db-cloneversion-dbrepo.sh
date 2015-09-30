#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst"
        echo
        exit
fi

source settings.sh

REPOSRC="tmp-sumo-db-dbrepo-create/central"
REPOSRC_SVN="tmp-sumo-db-dbrepo-create/central-svn"
REPOSRC_CVS="tmp-sumo-db-dbrepo-create/central-cvs"

echo -e "\n-> Test sumo db cloneversion with --dbrepo (repo commit, mode 'push')" >&2

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

$SUMO db --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode push -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-hg    --dbrepo "hg central-hg" --dbrepomode push -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-git   --dbrepo "git central-git" --dbrepomode push -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-svn   --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk" --dbrepomode push -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir local-cvs   --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" --dbrepomode push -y cloneversion ALARM R3-7 R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"

# create two files needed by other tests:
mkdir -p extra
hg -R local-hg diff --change tip > extra/PATCH
hg -R local-hg log -r tip --template '{desc}\n' > extra/LOGMESSAGE

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
echo
echo "==========================================="
echo "Test of subversion:"
echo
echo "Logs of local repository:"
echo "-------------------------------------------"
svn log local-svn | sed -e "s/^\([^|]\+\)|\([^|]\+\)|\([^|]\+\)|\([^|]\+\)/\1 | $DUSR | $DDATE |\4/"
echo
echo "Logs of central repository:"
echo "--> With subversion the central repository has ALWAYS"
echo "    the same set of patches as the working copy and "
echo "    aside from this we cannot simply show all logs of"
echo "    the repository without a working copy."
echo
echo "==========================================="
echo "Test of cvs:"
echo
echo "Logs of local repository:"
echo "-------------------------------------------"
cd local-cvs >/dev/null
cvs log 2>/dev/null | sed -e "s#$PWD_REAL##;s#$PWD_NICE##;s/\(date:\) [^;]\+/\1 $DDATE/;s/\(author:\) [^;]\+;/\1 $DUSR/;s/  commitid.*//;s/;$//"
cd .. /dev/null
echo
echo "Logs of central repository:"
echo "--> With cvs the central repository has ALWAYS"
echo "    the same set of patches as the working copy and "
echo "    aside from this we cannot simply show all logs of"
echo "    the repository without a working copy."
