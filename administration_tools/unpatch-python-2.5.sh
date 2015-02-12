#!/bin/sh

for f in ../bin/*; do
        sed -i '1 s/python2.5\>/python/' $f
done
