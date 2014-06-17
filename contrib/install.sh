#!/bin/sh

versions="3.14.8 3.14.12"

if [ -z "$2" ]; then
    echo "This script installs files from the sumo contrib directory"
    echo "usage: $0 [bin-directory] [share-directory]"
    exit 0
fi

bindir="$1"

if [ ! -d "$bindir" ]; then
    echo "error: $bindir not found"
    exit 1
fi

sharedir="$2"

if [[ "$sharedir" != *sumo ]]; then
    echo "error: $sharedir should end with 'sumo'"
    exit 1
fi

if [ ! -d "$sharedir" ]; then
    if [ -d `dirname $sharedir` ]; then
        echo "creating $sharedir..."
        mkdir $sharedir
    else
        echo "error: $sharedir not found"
        exit 1
    fi
fi

# scripts with an EPICS base version in their names:
versioned_scripts=`cd bin > /dev/null && ls *-[0-9]*`

# script templates that are used to create a script
# for each EPICS base version:
script_templates=`cd bin > /dev/null && ls *-`

# scripts that are generic:
generic_scripts=`cd bin > /dev/null && ls *[a-z]`

# copy all version specific scripts:
for src in $versioned_scripts; do
    cp -a bin/$src $bindir
done

# copy all generic scripts:
for src in $generic_scripts; do
    cp -a bin/$src $bindir
done

all_scripts="$versioned_scripts $generic_scripts"

# create version specific scripts from generic scripts
for file in $script_templates; do
    for ver in $versions; do
        src=bin/$file
        dst=$bindir/$file$ver
        all_scripts="$all_scripts $file$ver"
        cp $src $dst
        sed -i -e "s#^source \$SHARE/sumo-.*#source $sharedir/sumo-$ver.vars#" $dst
    done
done

cp -a share/*.config $sharedir

# for all *.vars files,
# if the file already exists keep the definition of SUMODIR:
for src in share/*.vars; do
    file=`basename $src`
    dst=$sharedir/$file
    if [ ! -e $dst ]; then
        cp $src $dst
    else
        SUMODIR=""
        source $dst
        cp $src $dst
        sed -i -e "s#^\( *SUMODIR\)=.*#\1=$SUMODIR#" $dst
    fi
done

# patch location of share directory in all scripts:
for script in $all_scripts; do
    sed -i -e "s#^SHARE=.*#SHARE=$sharedir#" $bindir/$script
done

