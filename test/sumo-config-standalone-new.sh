#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst sumo-build-new-1"
        echo
        exit
fi

source settings.sh

DBDIR="tmp-sumo-db-dbrepo-create/central"
BUILDDIR="tmp-sumo-build-new-1"

echo -e "\n-> Test sumo config standalone with sumo build new" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# create a dummy sumo.config
$SUMO --dbdir $PWD_NICE/$DBDIR --dbrepo "darcs $PWD_NICE/$DBDIR" --dbrepomode push --builddir $PWD_NICE/$BUILDDIR config make sumo.config

# now override it's settings
$SUMO -c sumo.config config standalone sumo

# now change DEPS.DB
$SUMO -c sumo.config -y db cloneversion ALARM R3-7 R3-9 darcs '*' | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"

# now create a new build
$SUMO -c sumo.config --no-make build new BASE:R3-14-12-2-1 ALARM:R3-9 EK:R2-2 BSPDEP_TIMER:R6-2 MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 2>&1

echo -e "\ncontents of sumo.config" 
cat sumo.config | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

echo -e "\nbuild directory tree (without darcs, maxdepth 2)"
find sumo -maxdepth 3 | sort -f -d | grep -v '_darcs\|\.hg\(\|ignore\)\|\.svn\|CVSROOT\|\.git\(\|ignore\)\|\.tmp\|\.bak\|\.coverage'

echo -e "\ncontent of DEPS.DB"
cat sumo/database/DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"

echo -e "\ncontent of BUILDS"
cat sumo/build/BUILDS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

