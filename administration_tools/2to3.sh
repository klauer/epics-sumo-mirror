#!/bin/sh

for f in ../python3/bin/*; do
        2to3 -w -n -f all -f idioms $f
done

for f in ../python3/sumolib/*.py; do
        2to3 -w -n -f all -f idioms $f
done

2to3 -n -f all -f idioms ../setup.py > ../setup-3.py
