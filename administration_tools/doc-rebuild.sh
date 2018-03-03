#!/bin/sh

ME=$(readlink -f "$0")
MYDIR=`dirname "$ME"`

cd "$MYDIR/../doc"

./make-png.sh
make clean -s
make html

cd "$MYDIR/.."

PY_MODULE="sumo_doc.py"
PY2_FILE="python2/sumolib/$PY_MODULE"
PY3_FILE="python3/sumolib/$PY_MODULE"

echo "creating $PY2_FILE"
$MYDIR/rst-extract.py --varname commands -o $PY2_FILE \
        -f doc/reference-sumo.rst \
        "maincommands:+" \
        'subcommands for maincommand "config":+' \
        'subcommands for maincommand "db":+' \
        'subcommands for maincommand "build":+'
$MYDIR/rst-extract.py --no-subchapters --varname completion \
        -f doc/reference-sumo.rst \
        "Command completion:-" >> $PY2_FILE
$MYDIR/rst-extract.py --no-subchapters --varname pager \
        -f doc/reference-sumo.rst \
        "The help pager:-" >> $PY2_FILE
$MYDIR/rst-extract.py --varname options \
        -f doc/reference-sumo.rst \
        "Options:-" >> $PY2_FILE
echo "creating $PY3_FILE"
cp -a $PY2_FILE $PY3_FILE

PY_MODULE="configuration_doc.py"
PY2_FILE="python2/sumolib/$PY_MODULE"
PY3_FILE="python3/sumolib/$PY_MODULE"
echo "creating $PY2_FILE"
$MYDIR/rst-extract.py --no-subchapters --varname text -o $PY2_FILE \
        -f doc/configuration-files.rst \
        "Configuration Files:=" 
echo "creating $PY3_FILE"
cp -a $PY2_FILE $PY3_FILE

