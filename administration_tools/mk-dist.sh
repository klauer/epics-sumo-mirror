#!/bin/bash
set -e
cd ..
python setup.py sdist --formats=zip,gztar
cd dist
cp `ls epics-sumo-*.tar.gz | tail -n 1` epics-sumo.tar.gz
cp `ls epics-sumo-*.zip | tail -n 1` epics-sumo.zip
