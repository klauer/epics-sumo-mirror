#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build find MCAN" >&2

TESTDIR=tmp-sumo-build-new-2

cd $TESTDIR > /dev/null

NL=""

function do_test {
    # $1: command
    echo -e "${NL}sumo $1:"
    $SUMO --dbdir . --builddir . $1
}

do_test "build find MCAN"
NL='\n'

do_test "build find MCAN ALARM:R3-7"

do_test "build find MCAN ALARM:R3-7 --detail 1"

do_test "build find MCAN ALARM:-R3-7"

do_test "build find MCAN ALARM:-R3-7 --detail 1"

do_test "build find MCAN ALARM:+R3-8"

do_test "build find MCAN ALARM:+R3-8 --detail 1"

do_test "build find MCAN:R2-6-3 XY:R1-2 --detail 1"

do_test "build find MCAN:R2-6-3 XY:R1-2 --detail 2"

do_test "build find BASE:R3-14-12-2-1 BSPDEP_TIMER:R6-2 --detail 2"

do_test "build find BASE:R3-14-12-2-1 BSPDEP_TIMER:R6-2 --detail 2 --all-builds"

do_test "build --dbdir . --builddir . find MCAN -b"

do_test "build --dbdir . --builddir . find MCAN -b --sort-build-dependencies-first"

do_test "build --dbdir . --builddir . find MCAN -b --sort-build-dependencies-last"

