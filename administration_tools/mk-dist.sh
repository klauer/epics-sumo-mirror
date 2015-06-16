#!/bin/bash
set -e
cd ..
python setup.py sdist --formats=zip,gztar
cd dist
cp `ls EPICS-sumo-*.tar.gz | tail -n 1` EPICS-sumo.tar.gz
cp `ls EPICS-sumo-*.zip | tail -n 1` EPICS-sumo.zip
