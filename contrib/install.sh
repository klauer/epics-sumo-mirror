#!/bin/sh

if [ "$1" = "-h" ]; then
    echo "This script installs files from the sumo contrib directory"
    echo "usage: $0 <sumodir> <sharedir> <bindir>"
    echo "  before you run the script configure variables in file 'config'"
    exit 0
fi

if [ -z "$1" ]; then
    echo "Error, <sumodir> missing"
    exit 1
fi
SUMODIR="$1"
shift
if [ -z "$1" ]; then
    echo "Error, <sharedir> missing"
    exit 1
fi
SHARE="$1"
shift
if [ -z "$1" ]; then
    echo "Error, <bindir> missing"
    exit 1
fi
BIN="$1"
shift

# some scripts are EPICS version specific get a number at
# the end of their filenames:
VERSIONS="3.14.8 3.14.12"

if [ ! -d "$BIN" ]; then
    echo "error: variable 'BIN': $BIN not found"
    exit 1
fi

if [ ! -d "$SHARE" ]; then
    echo "error: variable 'SHARE': $SHARE not found"
    exit 1
fi

if [ ! -d "$SUMODIR" ]; then
    echo "error: variable 'SUMODIR': $SUMODIR not found"
    exit 1
fi

# scripts with an EPICS base version in their names:
versioned_scripts=`cd bin > /dev/null && ls *-[0-9]*`

# script templates that are used to create a script
# for each EPICS base version:
script_templates=`cd bin > /dev/null && ls *-`

# scripts that are generic:
generic_scripts=`cd bin > /dev/null && ls *[a-z]`

# copy all version specific scripts:
for file in $versioned_scripts; do
    sed -e "s#^SHARE=.*#SHARE=$SHARE#" <bin/$file >$BIN/$file
    chmod 755 $BIN/$file
done

# copy all generic scripts:
for file in $generic_scripts; do
    sed -e "s#^SHARE=.*#SHARE=$SHARE#" <bin/$file >$BIN/$file
    chmod 755 $BIN/$file
done

# create version specific scripts from script templates
for file in $script_templates; do
    for ver in $VERSIONS; do
        sed -e "s#^SHARE=.*#SHARE=$SHARE#;s#^VERSION=.*#VERSION=$ver#" <bin/$file >$BIN/$file$ver
    chmod 755 $BIN/$file$ver
    done
done

cp -a share/*.config $SHARE

echo "# common variable definitions for contrib scripts" > $SHARE/sumo.vars
echo "SUMODIR=$SUMODIR" >> $SHARE/sumo.vars
echo "SHARE=$SHARE"     >> $SHARE/sumo.vars
cat share/sumo.vars     >> $SHARE/sumo.vars

echo "export PATH=$BIN:\$PATH" > PATH.sh

