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
    rm -rf pylint-2
else
    cd ..
fi

echo "creating rpm package..."

python3 setup.py bdist_rpm
if [ $docker = "yes" ]; then
    cp dist/*.rpm /root/dist 
    chmod 644 /root/dist/*.rpm
fi
