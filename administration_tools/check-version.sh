#!/bin/sh

cd ..

FILES="`ls python2/bin/*` `ls python3/bin/*` `ls python2/sumolib/[A-Za-z]*.py` `ls python3/sumolib/[A-Za-z]*.py` doc/conf.py setup.py"

grep "\"[^\"]\+\" \+\(#VERSION#\)" $FILES | column -t -s := | column -t
