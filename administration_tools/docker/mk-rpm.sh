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

DEPS=$(cat DEPS.RPM)

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

echo "creating rpm package..."
if [ -n "$DEPS" ]; then
    DEPS_ARG="--requires $DEPS"
fi
python3 setup.py bdist_rpm $DEPS_ARG
if [ $docker = "yes" ]; then
    cp dist/*.rpm /root/dist 
    chmod 644 /root/dist/*.rpm
fi
