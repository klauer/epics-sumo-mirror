#!/bin/sh

cd ../doc
./make-png.sh
make clean -s
make html
