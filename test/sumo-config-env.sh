#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo config show (environment expansion)" >&2

CONFIG=$ME-CONFIG.tmp

export DBDIR="my dbdir"
export DBREPO="my dbrepo"
export BUILDDIR="my builddir"
export LOCALBUILDDIR="my localbuilddir"

echo "create a config file with environment variables..."

$SUMO --no-default-config -y --dbdir '$DBDIR' --dbrepo '$DBREPO' --builddir '$BUILDDIR' --localbuilddir '$LOCALBUILDDIR' config make $CONFIG

echo
echo "content of config file:"
cat $CONFIG

echo "read by sumo with environment expansion:"
$SUMO --no-default-config -c $CONFIG config show

echo "now create with escaped backslashes..."

$SUMO --no-default-config -y --dbdir '\$DBDIR' --dbrepo '\$DBREPO' --builddir '\$BUILDDIR' --localbuilddir '\$LOCALBUILDDIR' config make $CONFIG

echo "content of config file:"
cat $CONFIG

echo "read by sumo with environment expansion:"
$SUMO --no-default-config -c $CONFIG config show

