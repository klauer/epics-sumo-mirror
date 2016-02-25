#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-releasefilename.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo build new and sumo db releasefilename." >&2

DEPSDIR=tmp-sumo-db-releasefilename

EXAMPLEDIR=tmp-$ME
if [ ! -d $EXAMPLEDIR ]; then
    mkdir $EXAMPLEDIR
fi
cd $EXAMPLEDIR > /dev/null
rm -f $EXAMPLEDIR/BUILDS.DB

$SUMO build --dbdir ../$DEPSDIR --builddir . --no-make new BASE:R3-14-12-2-1 MCAN:TAGLESS-2-6-1 ALARM:R3-7 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:R2-0 MISC_DBC:PATH-3-0  MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1

echo "BUILD file:"
cat BUILDS.DB

echo -e "\ndirectory tree (without darcs, maxdepth 2)"
find . -maxdepth 3 | sort -f -d | grep -v '_darcs\|\.hg\(\|ignore\)\|\.svn\|CVSROOT\|\.git\(\|ignore\)\|\.tmp\|\.bak\|\.coverage'
echo -e "\ncontents of RELEASE files\n"
for f in `find . -name '*RELEASE' | grep -v 'makeBase\(App\|Ext\)' | sort -f -d`; do echo -e "\nFILE: $f"; cat $f | sed -e "s#`pwd -P`#mysumo#"; done
