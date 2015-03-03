#!/bin/sh

for f in ../bin/*; do
        2to3 -w -n -f all -f idioms $f
done

for f in ../sumolib/*.py; do
        2to3 -w -n -f all -f idioms $f
done

2to3 -w -n -f all -f idioms ../setup.py
