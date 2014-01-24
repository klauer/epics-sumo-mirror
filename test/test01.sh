#!/bin/sh

PYTHON=$1

EXAMPLEDIR=tmp-test01
DARCSURL=rcsadm@aragon.acc.bessy.de
DARCSREPO=$DARCSURL:/opt/repositories/controls/darcs/epics

SUPPORTDIR=`pwd`/$EXAMPLEDIR
EPICSBASE=$SUPPORTDIR/BASE/R3-14-8-2-0

function darcs_get {
    # url tag dir
    if [ -z "$3" ]; then
        darcs get $1 $2 >/dev/null
    else
        darcs get $1 --tag $2 $3 >/dev/null
    fi
}

function darcs_support_get {
    # module(uppercase) reponame shorttag
    darcs_get $DARCSREPO/support/$2 R$3 $1/$3 
}

function patch_RELEASE {
    # params: dir
    sed -i $1/configure/RELEASE -e "s#^\(EPICS_BASE\)=.*#\1=$EPICSBASE#"
    sed -i $1/configure/RELEASE -e "s#^\(SUPPORT\)=.*#\1=$SUPPORTDIR#"
    sed -i $1/configure/RELEASE -e "s#^\(EPICS_SUPPORT\)=.*#\1=$SUPPORTDIR#"
    sed -i $1/configure/RELEASE -e "s#=/opt/Epics/R3.14.8/support#=$SUPPORTDIR#"
}

echo -e "\n-> Test pys-scan: checkout many modules and scan the directory tree." >&2
echo -e "\tIf run for the first time this may take a while..." >&2

if [ -d $EXAMPLEDIR ]; then
    echo -e "\t\n$EXAMPLEDIR already exists, skipping fresh checkout of modules..." >&2
else
    echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
    mkdir $EXAMPLEDIR
    cd $EXAMPLEDIR >/dev/null

    echo -e "\n\tdarcs checkout of EPICS 3.14.8.2.0" >&2
    mkdir BASE
    darcs_get $DARCSURL:/opt/csr/Epics/R3.14.8/base/3-14-8-2-0 R3-14-8-2-0 BASE/R3-14-8-2-0

    echo -e "\n\tdarcs checkout of alarm 3-0 and 3-5" >&2
    mkdir ALARM
    darcs_support_get ALARM alarm/base-3-14 3-0
    patch_RELEASE ALARM/3-0
    darcs_support_get ALARM alarm/base-3-14 3-5 
    patch_RELEASE ALARM/3-5

    echo -e "\n\tscp copy of asyn 4-15" >&2
    mkdir ASYN
    scp -r -p rcsadm@aragon.acc.bessy.de:/opt/csr/Epics/R3.14.8/support/asyn/4-15 ASYN/4-15 > /dev/null >/dev/null
    patch_RELEASE ASYN/4-15

    echo -e "\n\tdarcs checkout of bspdep 3-0" >&2
    mkdir -p BSPDEP
    darcs_support_get BSPDEP bspDep/base-3-14 3-0 
    patch_RELEASE BSPDEP/3-0

    echo -e "\n\tdarcs checkout of bspDep/cpuBoardInit 4-0" >&2
    mkdir -p BSPDEP/CPUBOARDINIT
    darcs_support_get BSPDEP/CPUBOARDINIT bspDep/cpuBoardInit 4-0 
    patch_RELEASE BSPDEP/CPUBOARDINIT/4-0

    echo -e "\n\tdarcs checkout of bspDep/timer 5-1" >&2
    mkdir -p BSPDEP/TIMER
    darcs_support_get BSPDEP/TIMER bspDep/timer 5-1 
    patch_RELEASE BSPDEP/TIMER/5-1

    echo -e "\n\tdarcs checkout of csm 3-8" >&2
    mkdir CSM
    darcs_support_get CSM csm/base-3-14-8 3-8 
    patch_RELEASE CSM/3-8

    echo -e "\n\tdarcs checkout of ek 2-0 and 2-1" >&2
    mkdir EK
    darcs_support_get EK ek/base-3-14 2-0 
    patch_RELEASE EK/2-0
    darcs_support_get EK ek/base-3-14 2-1 
    patch_RELEASE EK/2-1

    echo -e "\n\tscp copy of genSub 1-6-1" >&2
    mkdir GENSUB
    scp -r -p rcsadm@aragon.acc.bessy.de:/opt/csr/Epics/R3.14.8/support/genSub/1-6-1 GENSUB/1-6-1 > /dev/null
    patch_RELEASE GENSUB/1-6-1

    echo -e "\n\tdarcs checkout of mcan 2-0 and 2-3-18" >&2
    mkdir MCAN
    darcs_support_get MCAN mcan/base-3-14-8 2-0 
    patch_RELEASE MCAN/2-0
    darcs_support_get MCAN mcan/base-3-14-8 2-3-18 
    patch_RELEASE MCAN/2-3-18

    echo -e "\n\tdarcs checkout of misc 2-0 and 2-4" >&2
    mkdir MISC
    darcs_get $DARCSURL:/opt/csr/Epics/R3.14.8/support/misc/2-0 MISC/2-0 
    patch_RELEASE MISC/2-0
    darcs_support_get MISC misc/base-3-14 2-4 
    patch_RELEASE MISC/2-4

    echo -e "\n\tdarcs checkout of sequencer 2-0-12-1" >&2
    mkdir SEQ
    darcs_get $DARCSURL:/opt/csr/Epics/R3.14.8/support/seq/2-0-12-1 2-0-12-1 SEQ/2-0-12-1
    patch_RELEASE SEQ/2-0-12-1

    echo -e "\n\tdarcs checkout of soft support 2-0 and 2-5" >&2
    mkdir SOFT
    darcs_support_get SOFT soft/base-3-14 2-0 
    patch_RELEASE SOFT/2-0
    darcs_support_get SOFT soft/base-3-14 2-5 
    patch_RELEASE SOFT/2-5

    echo -e "\n\tdarcs checkout of vxStats 2-0" >&2
    mkdir VXSTATS
    darcs_support_get VXSTATS vxStats/base-3-14 2-0 
    patch_RELEASE VXSTATS/2-0
    cd ..
fi

$PYTHON ../bin/pys-scan -d $EXAMPLEDIR -g $EXAMPLEDIR all | sed -e "s#`pwd -P`##;s/,$/, /g"
