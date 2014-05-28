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

# all installed scripts:
installed_scripts=`cd bin > /dev/null && ls *-[0-9]*`

# copy all version specific scripts:
cp -a bin/*-[0-9]* $bindir

# create version specific scripts from generic scripts
for src in bin/*-; do
    file=`basename $src`
    for ver in $versions; do
        dst=$bindir/$file$ver
        installed_scripts="$installed_scripts $file$ver"
        cp $src $dst
        sed -i -e "s#^source.*#source $sharedir/sumo-$ver.vars#" $dst
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
for script in $installed_scripts; do
    sed -i -e "s#^SHARE=.*#SHARE=$sharedir#" $bindir/$script
done

