#!/bin/sh

mydir=`dirname $0`
cd $mydir

for f in ../python2/bin/*; do
        sed -i '1 s/python2.5\>/python/' $f
done
