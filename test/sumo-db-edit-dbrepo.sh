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

echo -e "\n-> Test sumo db edit with --dbrepo (repo commit, mode 'push')" >&2

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
# stupid git needs this:
git -C local-git config push.default simple
svn checkout -q file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk local-svn
cvs -d $PWD_NICE/$EXAMPLEDIR/central-cvs checkout sumo-database >/dev/null 2>&1 && mv sumo-database local-cvs

EDITOR="sed -e '11d;6d' -i"
LOGMSG='remove BSPDEP_TIMER dep from ALARM:R3-7'

$SUMO --dbdir local-darcs --dbrepo "darcs central-darcs" --dbrepomode push --editor "$EDITOR" db edit --logmsg "$LOGMSG"
$SUMO --dbdir local-hg    --dbrepo "hg central-hg"       --dbrepomode push --editor "$EDITOR" db edit --logmsg "$LOGMSG"
$SUMO --dbdir local-git   --dbrepo "git central-git"     --dbrepomode push --editor "$EDITOR" db edit --logmsg "$LOGMSG"
$SUMO --dbdir local-svn   --dbrepo "svn file://$PWD_NICE/$EXAMPLEDIR/central-svn/trunk" --dbrepomode push --editor "$EDITOR" db edit --logmsg "$LOGMSG"
# without "svn update" we don't see our own last log message:
(cd local-svn >/dev/null && svn update >/dev/null)
$SUMO --dbdir local-cvs   --dbrepo "cvs file://$PWD_NICE/$EXAMPLEDIR/central-cvs/sumo-database" --dbrepomode push --editor "$EDITOR" db edit --logmsg "$LOGMSG"

echo "==========================================="
echo "File diff (darcs):"
diff local-darcs/DEPS.DB.bak local-darcs/DEPS.DB
echo "File diff (hg):"
diff local-hg/DEPS.DB.bak local-hg/DEPS.DB
echo "File diff (git):"
diff local-git/DEPS.DB.bak local-git/DEPS.DB
echo "File diff (svn):"
diff local-svn/DEPS.DB.bak local-svn/DEPS.DB
echo "File diff (cvs):"
diff local-cvs/DEPS.DB.bak local-cvs/DEPS.DB
echo "==========================================="

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
