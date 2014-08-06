#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

EXAMPLEDIR=tmp-$ME
GLOBALSUPPORTDIR=rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.8/support
GLOBALBASEDIR=rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.8/base

BASEVER=3-14-8-2-0
SUPPORTDIR=`pwd`/$EXAMPLEDIR
EPICSBASE=$SUPPORTDIR/base/$BASEVER

function patch_RELEASE {
    # params: dir
    sed -i $1/configure/RELEASE -e "s#^\(EPICS_BASE\)=.*#\1=$EPICSBASE#"
    sed -i $1/configure/RELEASE -e "s#^\(SUPPORT\)=.*#\1=$SUPPORTDIR#"
    sed -i $1/configure/RELEASE -e "s#^\(EPICS_SUPPORT\)=.*#\1=$SUPPORTDIR#"
    sed -i $1/configure/RELEASE -e "s#=/opt/Epics/R3.14.8/support#=$SUPPORTDIR#"
}

function copy_base {
    # args: path
    echo -e "\n\tcopy EPICS base $BASEVER" >&2
    mkdir -p $EPICSBASE
    scp -r -p $GLOBALBASEDIR/$BASEVER `dirname $EPICSBASE`
}

function copy_support {
    # args: path
    echo -e "\n\tcopy $1" >&2
    mkdir -p $1
    scp -r -p $GLOBALSUPPORTDIR/$1 `dirname $1`
    patch_RELEASE $1
}

echo -e "\n-> Test sumo-scan: checkout many modules and scan the directory tree." >&2
echo -e "\tIf run for the first time this may take a while..." >&2

if [ -d $EXAMPLEDIR ]; then
    echo -e "\t\n$EXAMPLEDIR already exists, skipping fresh checkout of modules..." >&2
else
    echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
    mkdir $EXAMPLEDIR
    cd $EXAMPLEDIR >/dev/null
    copy_support alarm/3-0
    copy_support alarm/3-5
    copy_support asyn/4-15-bessy2
    copy_base 
    copy_support bspDep/cpuBoardInit/4-0
    copy_support bspDep/3-0
    copy_support bspDep/timer/5-1
    copy_support csm/3-8
    copy_support ek/2-0
    copy_support ek/2-1
    copy_support genSub/1-6-1
    copy_support mcan/2-3-18
    copy_support mcan/2-4
    copy_support misc/2-4
    copy_support misc/2-0
    copy_support seq/2-0-12-1
    copy_support soft/2-0
    copy_support soft/2-5
    copy_support vxStats/2-0
    cd ..
fi

#echo $PYTHON ../bin/sumo-scan -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
#$PYTHON ../bin/sumo-scan -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
$PYTHON ../bin/sumo-scan -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all | sed -e "s#`pwd -P`##"
