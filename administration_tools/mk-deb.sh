#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

APPLICATION=sumo

set -e

cd "$MYDIR"

if [ -e /root/dist ]; then
    # we are probably running within a docker container
    docker="yes"
else
    docker="no"
fi

if [ $docker = "yes" ]; then
    cd ../..
    echo "copying $APPLICATION dir into container..."
    # do not stop the script here if e.g. an editor swap file couldn't be
    # copied:
    cp -dR --preserve=mode,timestamps $APPLICATION my$APPLICATION || true
    cd my$APPLICATION
    rm -rf dist
else
    cd ..
fi

echo "creating python2 and python3 debian packages..."
python3 setup.py --command-packages=stdeb.command sdist_dsc --with-python2=True --with-python3=True bdist_deb
if [ $docker = "yes" ]; then
    cp deb_dist/*.deb /root/dist 
    chmod 644 /root/dist/*.deb
fi
