#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db find" >&2

DEPSDIR=tmp-sumo-db-convert

echo -e "find mcan:"
$SUMO db --dbdir $DEPSDIR find mcan | sed -e s#$PWD_NICE##

echo -e "\nfind mcan -b:"
$SUMO db --dbdir $DEPSDIR find mcan -b | sed -e s#$PWD_NICE##

echo -e "\nfind '^A' -b:"
$SUMO db --dbdir $DEPSDIR find '^A' -b | sed -e s#$PWD_NICE##

