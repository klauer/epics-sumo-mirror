#!/bin/bash
set -e

if [ -e /root/dist ]; then
    # we are probably running within a docker container
    docker="yes"
else
    docker="no"
fi

if [ $docker = "yes" ]; then
    cd ../..
    echo "copying sumo dir into container..."
    cp -dR --preserve=mode,timestamps sumo mysumo
    cd mysumo
    rm -rf dist
else
    cd ..
fi

echo "creating rpm package..."

python setup.py bdist_rpm
if [ $docker = "yes" ]; then
    cp dist/*.rpm /root/dist 
    chmod 644 /root/dist/*.rpm
fi
