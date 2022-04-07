#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build new with faulty DEPS.DB" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
# create an error in definition of BASE in DEPS.DB:
cat $DEPS | sed -e 's#repos/base/#repo/mybase/#' > $EXAMPLEDIR/DEPS.DB

cd $EXAMPLEDIR > /dev/null

# try to build with a single job, --jobs 1:
# this will check out ALARM, then BASE, then fail:
$SUMO build --dbdir . --builddir . --buildtag 001 --jobs 1 --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-3-gp BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 | sed -e "s#$PWD_REAL##g;s#$PWD_NICE##g" | sed -e 's/^darcs failed: *//' | sed -e '/^ *$/d;/^HINT:/d'

# try to build with a many jobs, --jobs 0:
# this will check out everything (or almost everything) except BASE, which then
# fails:
$SUMO build --dbdir . --builddir . --buildtag 002 --jobs 0 --no-make new BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:R2-6-3-gp BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0 2>&1 | sed -e "s#$PWD_REAL##g;s#$PWD_NICE##g" | sed -e 's/^darcs failed: *//' | sed -e '/^ *$/d;/^HINT:/d'

echo -e "\nnumber of directories created in first build (must be 1)"
find . -name *001 | wc -l

echo -e "\nTest if number of directories created in second build is greater than 1"
if [ "$(find . -name *002 | wc -l)" -gt 1 ]; then echo "ok"; else echo "fail"; fi

echo -e "\ncontents of BUILDS.DB:"
cat BUILDS.DB

