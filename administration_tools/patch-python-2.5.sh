#!/bin/sh

for f in ../bin/*; do
        sed -i '1 s/python\>/python2.5/' $f
done
