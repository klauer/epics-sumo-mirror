#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

set -e

cd "$MYDIR"

source docker.config

if [ -e /root/dist ]; then
    # we are probably running within a docker container
    docker="yes"
else
    docker="no"
fi

DEPS=$(cat DEPS.DEB)

if [ $docker = "yes" ]; then
    cd ../../..
    echo "copying $APPLICATION dir into container..."
    # do not stop the script here if e.g. an editor swap file couldn't be
    # copied:
    cp -dR --preserve=mode,timestamps $APPLICATION my$APPLICATION || true
    cd my$APPLICATION
    rm -rf dist
else
    cd ../..
fi

echo "creating python debian packages..."
if [ -n "$DEPS" ]; then
    DEPS_ARG="--depends3 $DEPS"
fi
python3 setup.py --command-packages=stdeb.command sdist_dsc --with-python3=True $DEPS_ARG bdist_deb 
if [ $docker = "yes" ]; then
    cp deb_dist/*.deb /root/dist 
    chmod 644 /root/dist/*.deb
fi
