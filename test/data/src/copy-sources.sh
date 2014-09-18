#!/bin/sh

# copy sources from host aragon to get modules we can use to test sumo-scan:

# this file is usually never executed, it is here to document how the files in
# this directory were created in the first place.

# Files bigger than 5kb are replaced by "dummy" files with just a few bytes in
# order to save disk space.

rm -rf base support

mkdir base
cp -a /opt/Epics/R3.14.12/base/3-14-12-2-1 base

mkdir support
cd support >/dev/null

SUPPORT=/opt/Epics/R3.14.12/support
mkdir alarm
cp -a $SUPPORT/alarm/3-7 alarm
cp -a $SUPPORT/alarm/3-8 alarm

mkdir -p apps/genericTemplate
cp -a $SUPPORT/apps/genericTemplate/3-0 apps/genericTemplate

mkdir -p apps/iocWatch
cp -a $SUPPORT/apps/iocWatch/3-0 apps/iocWatch

mkdir asyn
cp -a $SUPPORT/asyn/4-17-2 asyn

mkdir bessyRules
cp -a $SUPPORT/bessyRules/2-5 bessyRules

mkdir -p bspDep/cpuBoardInit
cp -a $SUPPORT/bspDep/cpuBoardInit/4-1 bspDep/cpuBoardInit

mkdir -p bspDep/timer
cp -a $SUPPORT/bspDep/timer/6-2 bspDep/timer

mkdir -p bspDep/VMEtas
cp -a $SUPPORT/bspDep/VMEtas/2-0 bspDep/VMEtas

mkdir -p csm
cp -a $SUPPORT/csm/4-1 csm

mkdir -p devIocStats
cp -a $SUPPORT/devIocStats/3-1-9-bessy3 devIocStats

mkdir -p ek
cp -a $SUPPORT/ek/2-2 ek

mkdir -p genSub
cp -a $SUPPORT/genSub/1-6-1 genSub

mkdir -p mcan
cp -a $SUPPORT/mcan/2-6-1 mcan
cp -a $SUPPORT/mcan/2-6-3-gp mcan

mkdir -p misc/dbc
cp -a $SUPPORT/misc/dbc/3-0 misc/dbc

mkdir -p misc/debugmsg
cp -a $SUPPORT/misc/debugmsg/3-0 misc/debugmsg

mkdir -p seq
cp -a $SUPPORT/seq/2-1-10 seq

mkdir -p soft/devHwClient
cp -a $SUPPORT/soft/devHwClient/3-0 soft/devHwClient

cd ..

# remove darcs repositories:
find . -name _darcs | xargs rm -rf 

# delete files not needed for sumo tests:
find . -name '*.cc'         -exec rm -f {} \;
find . -name '*.[choadti]'  -exec rm -f {} \;
find . -name '*.cpp'        -exec rm -f {} \;
find . -name '*.dbd'        -exec rm -f {} \;
find . -name '*.db'         -exec rm -f {} \;
find . -name '*.[ea]dl'     -exec rm -f {} \;
find . -name '*.fig'        -exec rm -f {} \;
find . -name '*.frame'      -exec rm -f {} \;
find . -name '*.gif'        -exec rm -f {} \;
find . -name '*.gz'         -exec rm -f {} \;
find . -name '*.html'       -exec rm -f {} \;
find . -name '*.obj'        -exec rm -f {} \;
find . -name '*.pdf'        -exec rm -f {} \;
find . -name '*.pl'         -exec rm -f {} \;
find . -name '*.png'        -exec rm -f {} \;
find . -name '*.so.*'       -exec rm -f {} \;
find . -name '*.so'         -exec rm -f {} \;
find . -name '*.template'   -exec rm -f {} \;
find . -name '*.txt'        -exec rm -f {} \;

# replace large files with smaller versions:
for f in `find -type f -size +5k`; do 
        rm -f $f
        echo "" > $f
done

tar -cvzf sources.tar.gz base support

rm -rf base support
