#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

REPODIR=`(cd data/repos > /dev/null && pwd)`
PWD=`pwd`

EXAMPLEDIR=tmp-$ME

function PATCH_RELEASE {
    # $1: path
    # uses $EPICSBASE and $SUPPORTDIR
    if [ -n "$EPICSBASE" ]; then
        sed -i $1/configure/RELEASE -e "s#^\(EPICS_BASE\)=.*#\1=$EPICSBASE#"
        sed -i $1/configure/RELEASE -e "s#^\(SUPPORT\)=.*#\1=$SUPPORTDIR#"
        sed -i $1/configure/RELEASE -e "s#^\(EPICS_SUPPORT\)=.*#\1=$SUPPORTDIR#"
    fi
}

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
    PATCH_RELEASE $1/$2
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

function PREPARE_REPO_GENERIC {
    # $1: source path 
    # $2: destination path
    # $3: tag
    echo -e "\t\tprepare $2..." >&2
    if [ ! -d `dirname $2` ]; then 
        mkdir -p `dirname $2`
    fi
    echo darcs get $REPODIR/$1 --tag $3 $2 >&2
    darcs get $REPODIR/$1 --tag $3 $2 1>&2
    # create fake binary directories:
    make -C $2 1>&2
    echo "PATCH_RELEASE $2" >&2
    PATCH_RELEASE $2
}

echo -e "\n-> Test sumo-scan: checkout many modules and scan the directory tree." >&2
echo -e "\tIf run for the first time this may take a while..." >&2



if [ -d $EXAMPLEDIR ]; then
    echo -e "\t\n$EXAMPLEDIR already exists, skipping fresh checkout of modules..." >&2
else
    echo -e "\n\tcreating directory $EXAMPLEDIR" >&2
    mkdir $EXAMPLEDIR
    cd $EXAMPLEDIR >/dev/null
    #echo -e "\t\tcopying 'base'..." >&2
    #cp -a $REPODIR/base . > /dev/null
    #cp -a $REPODIR/support . > /dev/null
    #echo -e "\t\tcopying 'support'..." >&2
    PREPARE_REPO_GENERIC base/3-14-12-2-1 base/3-14-12-2-1 3-14-12-2-1
    EPICSBASE=`pwd`/base/`ls base`
    SUPPORTDIR=`pwd`/support
    PREPARE_REPO support/alarm 3-7 
    PREPARE_REPO support/alarm 3-8 
    REPO_NEWTAG support/alarm 3-8 "mytag"
    PREPARE_PATH support/apps/genericTemplate 3-0
    PREPARE_REPO support/apps/iocWatch 3-0
    PREPARE_REPO support/asyn 4-17-2
    PREPARE_REPO support/bessyRules 2-5
    PREPARE_REPO support/bspDep/cpuBoardInit 4-1
    PREPARE_REPO support/bspDep/timer 6-2
    PREPARE_REPO support/bspDep/VMEtas 2-0
    PREPARE_REPO support/csm 4-1
    PREPARE_REPO support/devIocStats 3-1-9-bessy3
    PREPARE_REPO support/ek 2-2
    PREPARE_REPO support/genSub 1-6-1
    PREPARE_REPO support/mcan 2-6-1
    PREPARE_REPO support/mcan 2-6-3-gp
    PREPARE_REPO support/misc/dbc 3-0
    PREPARE_REPO support/misc/debugmsg 3-0
    PREPARE_REPO support/seq 2-1-10
    PREPARE_REPO support/soft/devHwClient 3-0
    cd ..
fi

#echo $PYTHON ../bin/sumo-scan -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
#$PYTHON ../bin/sumo-scan -d $EXAMPLEDIR -g $EXAMPLEDIR -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP -t all 
$PYTHON ../bin/sumo-scan -d "$EXAMPLEDIR/base $EXAMPLEDIR/support" -g "$EXAMPLEDIR/support $EXAMPLEDIR" -N TOP -N SUPPORT -N EPICS_SUPPORT -N TEMPLATE_TOP all > $EXAMPLEDIR/SCAN

cat $EXAMPLEDIR/SCAN | sed -e "s#`pwd -P`##;s#`pwd`##"
