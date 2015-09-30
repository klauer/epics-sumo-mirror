#!/bin/bash

set -e

# creates darcs repositories. 


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
    # without this sleep, darcs sometimes fails in a way that it doesn't see
    # changes in a local file.
    sleep 1
    #sync
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

# create mercurial repositories
function MK_HG
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
    if [ ! -e .hg ]; then
        hg init
        cp $SRCDIR/gitignore .gitignore
    fi
    if [ -n "$EPICSBASE" ]; then
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
    fi
    # run "hg add" when there seem to be new files:
    if hg status -u | grep '?' -q; then
        hg status -u -n | xargs hg add
    fi
    hg commit -m 'dummy mercurial commit' 
    hg tag $tag
    cd $old > /dev/null
  }

# create git repositories
function MK_GIT
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
    if [ ! -e .git ]; then
        git init
        cp $SRCDIR/gitignore .gitignore
    fi
    if [ -n "$EPICSBASE" ]; then
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
    fi
    # run "git add" when there seem to be new files:
    if git status -s -u | grep '?' -q; then
        git status --porcelain -u | sed -e 's/?? //' | xargs git add
    fi
    git commit -a -m 'dummy git commit' 
    git tag -a $tag -m 'my tag'
    cd $old > /dev/null
  }

# create subversion repositories
function MK_SVN
  { 
    old=`pwd`
    sourcepath="$1"
    destpath="$2"
    tag="$3"
    if [ ! -d $destpath ]; then
        mkdir -p $destpath
    fi
    svnadmin create --fs-type fsfs $destpath
    r_destpath=`(cd $destpath>/dev/null && pwd -P)`
    url="file://$r_destpath"
    cd $destpath/.. > /dev/null
    mkdir SVNTEMP && cd SVNTEMP > /dev/null
    mkdir trunk branches tags 
    cp -a $sourcepath/* trunk && cd trunk > /dev/null
    # cp $SRCDIR/svnignore .svnignore
    if [ -n "$EPICSBASE" ]; then
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
    fi
    cd .. > /dev/null
    svn import . $url -m "dummy svn commit"
    # make the cwd a SVN working copy:
    svn checkout --force $url .
    # set ignore properties
    source $SRCDIR/svnignore
    # create a tag:
    echo "svn copy $url/trunk $url/tags/$tag"
    svn copy $url/trunk $url/tags/$tag -m "my tag"
    cd ..  > /dev/null && rm -rf SVNTEMP
    cd $old > /dev/null
  }

# create subversion repositories
function MK_CVS
  { 
    old=`pwd`
    sourcepath="$1"
    destpath="$2"
    tag="$3"
    if [ ! -d $destpath ]; then
        mkdir -p $destpath
    fi
    root=`(cd $destpath>/dev/null && pwd -P)`
    project=`basename $destpath`
    cvs -d $root init
    cd $root/.. > /dev/null
    mkdir CVSTEMP && cd CVSTEMP > /dev/null
    cvs -d $root import -m 'initial version' $project dummy-user initial-version
    cd .. && rm -rf CVSTEMP
    mkdir CVSTEMP && cd CVSTEMP
    cvs -d $root checkout $project
    cp -a $sourcepath/* $project && cd $project > /dev/null
    cp $SRCDIR/cvsignore .cvsignore
    if [ -n "$EPICSBASE" ]; then
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
    fi
    find . -type d | grep -v '^.$' | grep -v CVS | xargs cvs add
    find . -type f | grep -v CVS | xargs cvs add
    cvs commit -m 'project files were added.'
    # create a tag:
    cvs tag $tag
    cd ../..  > /dev/null && rm -rf CVSTEMP
    cd $old > /dev/null
  }

# create just a directory
function MK_TAR
  { 
    old=`pwd`
    sourcepath="$1"
    tarname="$2"
    tardir="$3"

    if [ ! -d $tardir ]; then
        mkdir -p $tardir
    fi
    cd $tardir > /dev/null
    cp -a $sourcepath $tarname
    if [ -n "$EPICSBASE" ]; then
        cd $tarname > /dev/null
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        cd .. > /dev/null
    fi
    tar -czf $tarname.tar.gz $tarname
    rm -rf $tarname
    cd $old > /dev/null
  }

# create a patch file
function MK_PATCH
  {
    old=`pwd`
    source_base="$1"
    source1="$2"
    source2="$3"
    patchdir="$4"
    patchname="$5"

    if [ ! -d $patchdir/tmp ]; then
        mkdir -p $patchdir/tmp
    fi
    cd $patchdir/tmp > /dev/null
    cp -a $source_base/$source1 .
    if [ -n "$EPICSBASE" ]; then
        cd $source1 > /dev/null
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        cd .. > /dev/null
    fi
    cp -a $source_base/$source2 .
    if [ -n "$EPICSBASE" ]; then
        cd $source2 > /dev/null
        sed -i configure/RELEASE -e "s#^\(EPICS_BASE\) *=.*#\1=$EPICSBASE#"
        sed -i configure/RELEASE -e "s#^\(SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        sed -i configure/RELEASE -e "s#^\(EPICS_SUPPORT\) *=.*#\1=$SUPPORTDIR#"
        cd .. > /dev/null
    fi
    # diff has exit code 1 when there were differences:
    (diff -u $source1 $source2 > ../$patchname) || true
    cd .. > /dev/null
    rm -rf tmp
    cd $old > /dev/null
  }



mkdir base
mkdir -p support/apps

MK_DARCS $SRCDIR/base/3-14-12-2-1 base/3-14-12-2-1 R3-14-12-2-1

EPICSDIR=`dirname $PWD`/epics

EPICSBASE=$EPICSDIR/base/3-14-12-2-1
SUPPORTDIR=$EPICSDIR/support

MK_DARCS $SRCDIR/support/alarm/3-7                support/alarm            R3-7
MK_DARCS $SRCDIR/support/alarm/3-8                support/alarm            R3-8
MK_PATCH $SRCDIR/support/alarm 3-8 3-8-p          support  alarm-3-8-p.patch 
MK_DARCS $SRCDIR/support/apps/genericTemplate/3-0 support/apps/genericTemplate R3-0
MK_DARCS $SRCDIR/support/apps/iocWatch/3-0        support/apps/iocWatch        R3-0
MK_TAR   $SRCDIR/support/asyn/4-17-2 asyn-4-17-2  support/asyn 
MK_DARCS $SRCDIR/support/bessyRules/2-5           support/bessyRules       R2-5
MK_CVS   $SRCDIR/support/bspDep/cpuBoardInit/4-1  support/bspDep/cpuBoardInit      R4-1
MK_DARCS $SRCDIR/support/bspDep/timer/6-2         support/bspDep/timer     R6-2
MK_HG    $SRCDIR/support/bspDep/VMEtas/2-0        support/bspDep/VMEtas    R2-0
MK_HG    $SRCDIR/support/bspDep/VMEtas/2-1        support/bspDep/VMEtas    R2-1
MK_TAR   $SRCDIR/support/csm/4-1 csm-4-1          support/csm
MK_DARCS $SRCDIR/support/devIocStats/3-1-9-bessy3 support/devIocStats      R3-1-9-bessy3
MK_SVN   $SRCDIR/support/ek/2-2                   support/ek               R2-2
MK_DARCS $SRCDIR/support/genSub/1-6-1             support/genSub           R1-6-1
MK_DARCS $SRCDIR/support/mcan/2-6-1               support/mcan             R2-6-1
MK_DARCS $SRCDIR/support/mcan/2-6-3-gp            support/mcan             R2-6-3-gp
MK_DARCS $SRCDIR/support/misc/dbc/3-0             support/misc/dbc         R3-0
MK_GIT   $SRCDIR/support/misc/debugmsg/3-0        support/misc/debugmsg    R3-0
MK_GIT   $SRCDIR/support/misc/debugmsg/3-1        support/misc/debugmsg    R3-1
MK_DARCS $SRCDIR/support/seq/2-1-10               support/seq              R2-1-10
MK_TAR   $SRCDIR/support/soft/devHwClient/3-0 devHwClient-3-0 support/soft
