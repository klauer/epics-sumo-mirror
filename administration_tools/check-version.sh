#!/bin/sh

cd ..

FILES="`ls bin/*` `ls sumo/[A-Za-z]*.py` doc/conf.py setup.py"

grep "\"[^\"]\+\" \+\(#VERSION#\)" $FILES | column -t -s := | column -t
