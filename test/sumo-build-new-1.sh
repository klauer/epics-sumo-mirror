#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build new with a module with patchfile" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../$DEPS .

$SUMO --dbdir . --builddir . config make sumo.config

# add a new version of ALARM R3-8-patch that uses a patchfile:
# this creates the output "added module":
$SUMO -y -c sumo.config db cloneversion ALARM R3-8-modified R3-8-patch patches=$REPODIR/support/alarm-3-8-p.patch | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"

$SUMO -c sumo.config build  --buildtag-stem BASE --no-make new BASE:R3-14-12-2-1 2>&1 
$SUMO -c sumo.config build  state BASE-001 stable 2>&1 
$SUMO -c sumo.config build  --buildtag-stem MYAPP --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-patch EK:R2-2 MCAN:R2-6-3-gp BSPDEP_CPUBOARDINIT:R4-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified CSM:TAR-4-1 MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 
$SUMO -c sumo.config build  state MYAPP-001 testing 2>&1 

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | sort -f -d | grep -v '_darcs\|\.hg\(\|ignore\)\|\.svn\|CVSROOT\|\.git\(\|ignore\)\|\.tmp\|\.bak\|\.coverage'
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name RELEASE | grep -v 'makeBase\(App\|Ext\)' | sort -f -d `; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`#mysumo#"; done
echo -e "\ncontent of ALARM Makefile:"
cat ALARM/R3-8-patch*/Makefile
echo -e "\ncontent of BUILDS"
cat BUILDS.DB
echo -e "\ncontent of Makefile-BASE-001"
cat Makefile-BASE-001 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"
echo -e "\ncontent of Makefile-MYAPP-001"
cat Makefile-MYAPP-001 | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

