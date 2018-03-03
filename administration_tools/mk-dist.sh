#!/bin/bash
set -e
cd ..
python setup.py sdist --formats=zip,gztar
