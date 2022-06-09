#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo config make --getmodules" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

NL=""

function do_test {
    # $1: command
    # $2: ignore return code
    echo -e "${NL}sumo $1:"
    $SUMO --dbdir . --builddir . $1 2>&1
    if [ -n "$2" ]; then
        true
    fi
}

# first create a MODULES file:
MODULES_FILE=CONFIG-MAKE-3-MODULES

do_test "-y -m MCAN:R2-6-3 -m BASE:R3-14-12-2-1 config make $MODULES_FILE module --exceptions"

echo "Contents of MODULES file before changes:"
cat $MODULES_FILE

do_test "-y -c $MODULES_FILE config make $MODULES_FILE module --getmodules MYAPP-002"
echo "Contents of MODULES after changes:"
cat $MODULES_FILE

do_test "-y -m MCAN:R2-6-3 -m BASE:R3-14-12-2-1 -m BSPDEP_TIMER:1 -m CSM:2 config make $MODULES_FILE module"

echo "Contents of MODULES file before changes:"
cat $MODULES_FILE

do_test "-y -c $MODULES_FILE config make $MODULES_FILE module --getmodules MYAPP-002"
echo "Contents of MODULES after changes:"
cat $MODULES_FILE

do_test "-y -m MCAN:R2-6-3 -m BASE:R3-14-12-2-1 -m BSPDEP_TIMER:1 -m CSM:2 -m AB:1 -m XY:2 config make $MODULES_FILE module"

echo "Contents of MODULES file before changes:"
cat $MODULES_FILE

do_test "-y -c $MODULES_FILE config make $MODULES_FILE module --getmodules MYAPP-002"
echo "Contents of MODULES after changes:"
cat $MODULES_FILE


