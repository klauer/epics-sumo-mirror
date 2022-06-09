#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build getmodules" >&2

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

do_test "build getmodules MYAPP-001 MCAN:R1-2-3"
NL='\n'

do_test "build getmodules MYAPP-002 MCAN:R1-2-3"

do_test "build getmodules MYAPP-002 MCAN:R1-2-3 BSPDEP_TIMER CSM"

do_test "build getmodules MYAPP-002 MCAN:R1-2-3 BSPDEP_TIMER CSM AB:1 CD:2" yes



