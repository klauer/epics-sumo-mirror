#!/bin/sh

config_version=`grep '^version' ../doc/conf.py | sed -e 's/^.*"\([^"]\+\)".*/\1/'`

setup_version=`grep my_version= ../setup.py | sed -e 's/^.*"\([^"]\+\)".*/\1/'`

scan_version=`grep my_version= ../bin/sumo-scan | sed -e 's/^.*"\([^"]\+\)".*/\1/'`

db_version=`grep my_version= ../bin/sumo-db | sed -e 's/^.*"\([^"]\+\)".*/\1/'`

build_version=`grep my_version= ../bin/sumo-build | sed -e 's/^.*"\([^"]\+\)".*/\1/'`

err="no"

if [ $setup_version != $config_version ]; then err="yes"; fi
if [ $setup_version != $scan_version ]; then err="yes"; fi
if [ $setup_version != $db_version ]; then err="yes"; fi
if [ $setup_version != $build_version ]; then err="yes"; fi

if [ "$err" != "no" ]; then
        echo "error: setup.py   version is     : $setup_version"
        echo "       conf.py    version is     : $config_version"
        echo "       sumo-scan  version is     : $scan_version"
        echo "       sumo-db    version is     : $db_version"
        echo "       sumo-build version is     : $build_version"
        exit 1
fi
echo "version check OK"
exit 0

