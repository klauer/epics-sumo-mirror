#!/bin/sh

# creates a fake epics support directory.

REPODIR=`(cd ../repos > /dev/null && pwd)`
PWD=`pwd`

function PREPARE_PATH {
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

function REPO_NEWTAG {
    # $1: path
    # $2: version
    # $3: tag
    (cd $1/$2 && darcs tag $3) > /dev/null
}

function PREPARE_REPO {
    # $1: path
    # $2: version
    PREPARE_REPO_GENERIC $1 "$1/$2" $2
}

function PREPARE_REPO_MISSING {
    # $1: path
    # $2: version
    PREPARE_REPO_GENERIC $1 "$1/$2" $2
    # create a repo whose default source repo doesn't exist
    echo "XX" > "$1/$2/_darcs/prefs/defaultrepo"
}

function PREPARE_REPO_TAGLESS {
    # $1: path
    # $2: version
    PREPARE_REPO_GENERIC $1 "$1/$2" $2
    # remove the tag
    yes | darcs obliterate --repodir "$1/$2" --patch "R$2" 1>&2
}

function PREPARE_REPO_GENERIC {
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

mkdir base
mkdir -p support/apps

PREPARE_REPO_GENERIC base/3-14-12-2-1 base/3-14-12-2-1 3-14-12-2-1
PREPARE_REPO support/alarm 3-7 
PREPARE_REPO support/alarm 3-8 
REPO_NEWTAG support/alarm 3-8 "mytag"
PREPARE_PATH support/apps/genericTemplate 3-0
PREPARE_REPO support/apps/iocWatch 3-0
PREPARE_REPO support/asyn 4-17-2
PREPARE_REPO support/bessyRules 2-5
PREPARE_REPO support/bspDep/cpuBoardInit 4-1
PREPARE_REPO_MISSING support/bspDep/timer 6-2
PREPARE_REPO support/bspDep/VMEtas 2-0
PREPARE_REPO support/csm 4-1
PREPARE_REPO support/devIocStats 3-1-9-bessy3
PREPARE_REPO_TAGLESS support/ek 2-2
PREPARE_REPO support/genSub 1-6-1
PREPARE_REPO support/mcan 2-6-1
PREPARE_REPO support/mcan 2-6-3-gp
PREPARE_REPO support/misc/dbc 3-0
PREPARE_REPO support/misc/debugmsg 3-0
PREPARE_REPO support/seq 2-1-10
PREPARE_REPO support/soft/devHwClient 3-0

