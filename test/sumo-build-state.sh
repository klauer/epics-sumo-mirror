#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build state (query)" >&2

SUPPORTDIR=tmp-sumo-build-new-0

echo "state of AUTO-001:"
$SUMO build --builddir $SUPPORTDIR state AUTO-001
echo
echo "state of AUTO-002:"
$SUMO build --builddir $SUPPORTDIR state AUTO-002
