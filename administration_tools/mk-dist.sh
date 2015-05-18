#!/bin/bash
set -e
cd ..
python setup.py sdist --formats=zip,gztar
cd dist
cp `ls sumo-*.tar.gz | tail -n 1` sumo.tar.gz
cp `ls sumo-*.zip | tail -n 1` sumo.zip
