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

echo "creating debian package..."
python setup.py --command-packages=stdeb.command bdist_deb
if [ $docker = "yes" ]; then
    cp deb_dist/*.deb /root/dist 
    chmod 644 /root/dist/*.deb
fi
