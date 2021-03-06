#!/bin/bash

set -e

# creates a fake epics support directory.

REPODIR=`(cd ../repos > /dev/null && pwd)`
OLD_PWD=`pwd`

function MK_PATH {
    # $1: path
    # $2: version
    echo -e "\t\tprepare $1/$2..." >&2
    if [ ! -d $1 ]; then 
        mkdir -p $1
    fi
    echo cp -a $REPODIR/$1 $1/$2 >&2
    cp -a $REPODIR/$1 $1/$2 >&2
    rm -rf $1/$2/_darcs
}

function MK_DARCS_NEWTAG {
    # $1: path
    # $2: version
    # $3: tag
    (cd $1/$2 && darcs tag $3) > /dev/null
}

function MK_DARCS {
    # $1: path
    # $2: version
    MK_DARCS_GENERIC $1 "$1/$2" $2
}

function MK_DARCS_MISSING {
    # $1: path
    # $2: version
    MK_DARCS_GENERIC $1 "$1/$2" $2
    # create a repo whose default source repo doesn't exist
    echo "XX" > "$1/$2/_darcs/prefs/defaultrepo"
}

function MK_DARCS_TAGLESS {
    # $1: path
    # $2: version
    MK_DARCS_GENERIC $1 "$1/$2" $2
    # remove the tag
    yes | darcs obliterate --repodir "$1/$2" --patch "R$2" 1>&2
}

function MK_DARCS_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    echo darcs get $REPODIR/$1 --tag $3 $2 >&2
    darcs get $REPODIR/$1 --tag R$3 $2 1>&2
    # create fake binary directories:
    make -C $2 1>&2
}

function MK_HG_TAGLESS {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_HG_GENERIC $1 "$1/$2" $3
    echo "#some change" >> "$1/$2/Makefile"
    hg commit -R "$1/$2" -m 'some changes'
}

function MK_HG {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_HG_GENERIC $1 "$1/$2" $3
}

function MK_HG_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    echo hg clone $REPODIR/$1 $2 -u $3 >&2
    hg clone $REPODIR/$1 $2 -u $3 >&2
    # create fake binary directories:
    make -C $2 1>&2
}

function MK_GIT_TAGLESS {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_GIT_GENERIC $1 "$1/$2" $3
    echo "#some change" >> "$1/$2/Makefile"
    (cd "$1/$2" && git commit -m 'some changes')
}

function MK_GIT {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_GIT_GENERIC $1 "$1/$2" $3
}

function MK_GIT_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    echo git clone $REPODIR/$1 $2 >&2
    git clone $REPODIR/$1 $2 >&2
    (cd $2 && git checkout $3) >&2
    # create fake binary directories:
    make -C $2 1>&2
}

function MK_SVN {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_SVN_GENERIC $1 "$1/$2" $3
}

function MK_SVN_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    if [ -z "$3" ]; then
            url="file://$REPODIR/$1/trunk"
    else
            url="file://$REPODIR/$1/tags/$3"
    fi
    echo svn checkout $url $2 >&2
    svn checkout $url $2 >&2
    # create fake binary directories:
    make -C $2 1>&2
}

function MK_CVS {
    # $1: path
    # $2: subdir
    # $3: tag
    MK_CVS_GENERIC $1 "$1/$2" $3
}

function MK_CVS_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    if [ -z "$3" ]; then
           rev=""
    else
           rev="-r $3"
    fi
    # note: CVS repos created by mk-repos.sh have the path:
    # /<directories>/<project>/<project>
    # Since CVS is intended to have more than one project under a single
    # CVS root directory.
    root=$REPODIR/$1
    repo=`basename $REPODIR/$1`
    echo cvs -d $root checkout $rev $repo >&2
    cvs -d $root checkout $rev $repo >&2
    mv $repo $2
    # create fake binary directories:
    make -C $2 1>&2
}

function MK_TAR {
    # $1: tarfile
    # $2: destination-dir
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d $2 ]; then 
        mkdir -p $2
    fi
    tar_filename=`basename $1`
    tar_base=`echo $tar_filename | sed -e 's/\..*//'`
    module=`echo $tar_base | sed -e 's/-.*//'`
    version=`echo $tar_base | sed -e 's/[^-]\+-//'`

    cd $2 > /dev/null
    pwd
    cp $REPODIR/$1 .
    touch DIRLIST-NEW
    ls > DIRLIST-OLD
    tar -xzf `basename $1`
    ls > DIRLIST-NEW
    newdir=`diff DIRLIST-OLD DIRLIST-NEW | grep '>' | sed -e 's/> //'`
    rm -f DIRLIST-OLD DIRLIST-NEW

    if [ ! -d $module ]; then
        mkdir -p $module
    fi
    pwd
    mv $newdir $module/$version
    # create fake binary directories:
    make -C $module/$version 1>&2
    cd $OLD_PWD > /dev/null
}

mkdir base
mkdir -p support/apps

MK_DARCS_GENERIC base/3-14-12-2-1 base/3-14-12-2-1 3-14-12-2-1
MK_DARCS         support/alarm 3-7 
MK_DARCS         support/alarm 3-8 
MK_DARCS_NEWTAG  support/alarm 3-8 "R3-8-modified"
MK_PATH          support/apps/genericTemplate 3-0
MK_DARCS         support/apps/iocWatch 3-0
MK_TAR           support/asyn/asyn-4-17-2.tar.gz support
MK_DARCS         support/bessyRules 2-5
MK_CVS           support/bspDep/cpuBoardInit 4-1 R4-1
MK_DARCS_MISSING support/bspDep/timer 6-2
MK_HG            support/bspDep/VMEtas 2-0 R2-0
MK_HG            support/bspDep/VMEtas 2-1 R2-1
MK_HG_TAGLESS    support/bspDep/VMEtas 2-1-modified R2-1
MK_TAR           support/csm/csm-4-1.tar.gz support
MK_DARCS         support/devIocStats 3-1-9-bessy3
MK_SVN           support/ek 2-2 R2-2
MK_DARCS         support/genSub 1-6-1
MK_DARCS_TAGLESS support/mcan 2-6-1
MK_DARCS         support/mcan 2-6-3-gp
MK_PATH          support/misc/dbc 3-0
MK_GIT           support/misc/debugmsg 3-0 R3-0
MK_GIT           support/misc/debugmsg 3-1 R3-1
MK_DARCS         support/seq 2-1-10
MK_TAR           support/soft/devHwClient-3-0.tar.gz support/soft

