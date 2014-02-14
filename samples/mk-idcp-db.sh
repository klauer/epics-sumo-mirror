#!/bin/sh

MYDIR=`pwd`

cd ..
. PATH.sh

cd $MYDIR

DBFILE=R3-14-8.DB
OUT=IDCP.DB

python2.5 `which sumo-db` --db $DBFILE --arch vxWorks-ppc603 distribution unstable MCAN ASYN BSPDEP_CPUBOARDINIT CSM EK GENSUB SEQ VXSTATS > $OUT

