#!/bin/sh

# creates darcs repositories. Note that the directories also contain binaries
# that are ignored by darcs.


SRCDIR=`(cd ../src >/dev/null && pwd)`
PWD=`pwd`

# create darcs repositories
function MK_DARCS
  { 
    old=`pwd`
    sourcepath="$1"
    destpath="$2"
    tag="$3"
    if [ ! -d $destpath ]; then
        mkdir -p $destpath
    fi
    cd $destpath > /dev/null
    cp -a $sourcepath/* .
    #echo "DIR : $sourcepath"
    if [ ! -e _darcs ]; then
        darcs init
        cp $SRCDIR/boring _darcs/prefs/boring
    fi
    if [ -n "$EPICSBASE" ]; then
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
    fi
    # run "darcs add" when there seem to be new files:
    if darcs whatsnew -l | grep '^a' -q; then
        darcs add -r [^_]*
        # [^_]* : skip "_darcs"
    fi
    darcs record -m 'dummy darcs record' -a 
    darcs tag $tag
    cd $old > /dev/null
  }

mkdir base
mkdir -p support/apps

MK_DARCS $SRCDIR/base/3-14-12-2-1 base/3-14-12-2-1 R3-14-12-2-1

EPICSBASE=`pwd`/`ls base`
SUPPORTDIR=`pwd`/support

MK_DARCS $SRCDIR/support/alarm/3-7                support/alarm            R3-7
MK_DARCS $SRCDIR/support/alarm/3-8                support/alarm            R3-8
MK_DARCS $SRCDIR/support/apps/genericTemplate/3-0 support/apps/genericTemplate R3-0
MK_DARCS $SRCDIR/support/apps/iocWatch/3-0        support/apps/iocWatch        R3-0
MK_DARCS $SRCDIR/support/asyn/4-17-2              support/asyn             R4-17-2
MK_DARCS $SRCDIR/support/bessyRules/2-5           support/bessyRules       R2-5
MK_DARCS $SRCDIR/support/bspDep/cpuBoardInit/4-1  support/bspDep/cpuBoardInit      R4-1
MK_DARCS $SRCDIR/support/bspDep/timer/6-2         support/bspDep/timer     R6-2
MK_DARCS $SRCDIR/support/bspDep/VMEtas/2-0        support/bspDep/VMEtas    R2-0
MK_DARCS $SRCDIR/support/csm/4-1                  support/csm              R4-1
MK_DARCS $SRCDIR/support/devIocStats/3-1-9-bessy3 support/devIocStats      R3-1-9-bessy3
MK_DARCS $SRCDIR/support/ek/2-2                   support/ek               R2-2
MK_DARCS $SRCDIR/support/genSub/1-6-1             support/genSub           R1-6-1
MK_DARCS $SRCDIR/support/mcan/2-6-1               support/mcan             R2-6-1
MK_DARCS $SRCDIR/support/mcan/2-6-3-gp            support/mcan             R2-6-3-gp
MK_DARCS $SRCDIR/support/misc/dbc/3-0             support/misc/dbc         R3-0
MK_DARCS $SRCDIR/support/misc/debugmsg/3-0        support/misc/debugmsg    R3-0
MK_DARCS $SRCDIR/support/seq/2-1-10               support/seq              R2-1-10
MK_DARCS $SRCDIR/support/soft/devHwClient/3-0     support/soft/devHwClient R3-0

