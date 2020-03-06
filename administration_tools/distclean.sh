#!/bin/bash

# This script removes various generated files that are not under version
# control. This goal is to put the working copy in a state that it only
# contains version controled files.

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

(cd $MYDIR/../test && make distclean -sj)
(cd $MYDIR/../doc && make clean)
rm -f $MYDIR/*.LOG

$MYDIR/cleanup-distdirs.sh

find $MYDIR/../python2 -name '*.pyc' | xargs rm -f
find $MYDIR/../python3 -name '*.pyc' | xargs rm -f

rm -rf $MYDIR/../python2/sumolib/data
rm -rf $MYDIR/../python3/sumolib/data

rm -f $MYDIR/setup.pyc

rm -rf $MYDIR/../build

rm -f $MYDIR/../doc/Modules*.png
rm -f $MYDIR/../doc/Sumo-overview.png

rm -f $MYDIR/../MANIFEST
rm -f $MYDIR/../python2/sumolib/configuration_doc.py
rm -f $MYDIR/../python2/sumolib/sumo_doc.py
rm -f $MYDIR/../python3/sumolib/configuration_doc.py
rm -f $MYDIR/../python3/sumolib/sumo_doc.py

find $MYDIR/.. -name *.sw? | xargs rm -f


