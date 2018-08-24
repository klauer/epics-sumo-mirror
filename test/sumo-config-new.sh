#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo config new." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# create config file:
$SUMO --no-default-config config new sumo-empty empty

echo "generated config file:"
cat sumo.config | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"
mv sumo.config sumo.config.empty

echo "generated DEPS.DB:"
cat sumo-empty/database/DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

# create config file:
$SUMO --no-default-config config new sumo-github github

echo "generated config file:"
cat sumo.config | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"
mv sumo.config sumo.config.github

echo "generated DEPS.DB:"
cat sumo-github/database/DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##"

