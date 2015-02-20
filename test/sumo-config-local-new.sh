#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-dbrepo-create.tst sumo-build-new-1"
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

DBDIR="tmp-sumo-db-dbrepo-create/central"
BUILDDIR="tmp-sumo-build-new-1"

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`

echo -e "\n-> Test sumo config local with sumo build new" >&2

EXAMPLEDIR=tmp-$ME

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# create a dummy sumo.config
$SUMO --dbdir $PWD_NICE/$DBDIR --dbrepo "darcs $PWD_NICE/$DBDIR" --dbrepomode push --builddir $PWD_NICE/$BUILDDIR config make sumo.config

# now override it's settings
$SUMO -c sumo.config config local sumo

# now change DEPS.DB
$SUMO -c sumo.config -y db cloneversion ALARM R3-7 R3-9 darcs '*' 

# now create a new build
$SUMO -c sumo.config --no-make build new BASE:R3-14-12-2-1 ALARM:R3-9 BSPDEP_TIMER:R6-2 MISC_DBC:PATH-3-0

echo -e "\ncontents of sumo.config" 
cat sumo.config | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

echo -e "\nbuild directory tree (without darcs, maxdepth 2)"
find sumo -maxdepth 3 | grep -v '_darcs\|\.hg\(\|ignore\)\|\.git\(\|ignore\)\|\.tmp\|\.bak\|\.coverage'

echo -e "\ncontent of DEPS.DB"
cat sumo/database/DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

echo -e "\ncontent of BUILDS"
cat sumo/build/BUILDS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"
