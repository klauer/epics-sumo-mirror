#!/bin/sh

MYDIR=`pwd`
DB1=R3-14-8.DB
DB2=R3-14-12.DB
DB=ALL.DB

cd ..
. PATH.sh

cd $MYDIR

python2.5 `which sumo-db` --dumpdb --db $DB1 merge $DB2 > $DB
