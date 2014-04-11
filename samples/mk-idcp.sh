#!/bin/sh

MYDIR=`pwd`

cd ..
. PATH.sh

cd $MYDIR

DBFILE=R3-14-12.DB

OUT=IDCP.CONFIG
OUT2=IDCP.DB

python2.5 `which sumo-build` --db $DBFILE --arch vxWorks-ppc603 --maxstate unstable try MCAN ASYN BSPDEP_CPUBOARDINIT CSM EK GENSUB SEQ VXSTATS > $OUT

python2.5 `which sumo-db` --db $DBFILE --update-config $OUT filter > $OUT2
