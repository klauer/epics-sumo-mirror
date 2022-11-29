#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo-scan all with faulty buildtree" >&2

SRCDIR=tmp-sumo-build-new-2
TESTDIR=tmp-sumo-scan-all-err

if [ ! -d $TESTDIR ]; then
    # copy $SRCDIR for our test:
    cp -a $SRCDIR $TESTDIR
    cd $TESTDIR > /dev/null
    for f in `find . -name RELEASE`; do
        sed -i $f -e "s#$SRCDIR#$TESTDIR#g"
    done
    # create an error in RELEASE file:
    echo "include xyz" >> ALARM/R3-8*/configure/RELEASE
    cd .. > /dev/null
fi

$SUMO_SCAN --ignore-changes 'configure/RELEASE' -d $TESTDIR --group-basedir `pwd -P`/$TESTDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all --buildtag MYAPP-001 2>$TESTDIR/STDERR | sed -e "s#$(pwd -P)##;s#$PWD_NICE##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#" > $TESTDIR/STDOUT

bt='`'
cat $TESTDIR/STDERR | sed -e "s#$(pwd -P)##;s#$PWD_NICE##;s/$bt/'/g"
cat $TESTDIR/STDOUT

