#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=`dirname "$ME"`

cd "$MYDIR/.."

PY_MODULE="sumo_doc.py"
PY_FILE="sumolib/$PY_MODULE"

echo "creating $PY_FILE"
$MYDIR/rst-extract.py --varname commands -o $PY_FILE \
        -f doc/reference-sumo.rst \
        "maincommands:+" \
        'subcommands for maincommand "config":+' \
        'subcommands for maincommand "db":+' \
        'subcommands for maincommand "build":+'
$MYDIR/rst-extract.py --no-subchapters --varname completion \
        -f doc/reference-sumo.rst \
        "Command completion:-" >> $PY_FILE
$MYDIR/rst-extract.py --no-subchapters --varname pager \
        -f doc/reference-sumo.rst \
        "The help pager:-" >> $PY_FILE
$MYDIR/rst-extract.py --varname options \
        -f doc/reference-sumo.rst \
        "Options:-" >> $PY_FILE

PY_MODULE="configuration_doc.py"
PY_FILE="sumolib/$PY_MODULE"
echo "creating $PY_FILE"
$MYDIR/rst-extract.py --no-subchapters --varname text -o $PY_FILE \
        -f doc/configuration-files.rst \
        "Configuration Files:=" 

