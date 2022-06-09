#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build showmodules" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

NL=""

function do_test {
    # $1: command
    echo -e "${NL}sumo $1:"
    $SUMO --dbdir . --builddir . $1 2>&1
}

do_test "build showmodules MYAPP-001"
NL='\n'

do_test "build showmodules MYAPP-001 --lines"

do_test "build showmodules MYAPP-001 -b --lines"

do_test "build showmodules"

do_test "build showmodules --all-builds"

do_test "build showmodules -b --all-builds"

do_test "build showmodules -b --lines --all-builds"

do_test "build showmodules --sort-build-dependencies-last --all-builds"

