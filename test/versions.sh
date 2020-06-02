#!/bin/bash

SCRIPT_FULL_NAME=$(readlink -e $0)
MYDIR=$(dirname $SCRIPT_FULL_NAME)
MYNAME=$(basename $SCRIPT_FULL_NAME)

echo -n "host: "; hostname -f
lsb_release -a 2>&1 | grep -v "No LSB modules"
echo "-------------------------------------------------"
echo -n "sumo: "; grep VERSION ../setup.py  | sed -e 's/^[^"]\+"//;s/".*//'
echo -n "bash: "; bash --version | head -n 1 | sed -e 's/^[^0-9]\+//'
echo -n "python: "; python3 --version 2>&1 | sed -e 's/^[^0-9]\+//'
echo -n "cvs: "; cvs --version | grep '[0-9]\+\.[0-9]\+' | sed -e 's/^[^0-9]\+//'
echo -n "subversion: "; svn --version | head -n 1 | sed -e 's/^[^0-9]\+//'
echo -n "darcs ";darcs --version
echo -n "mercurial: "; hg --version | head -n 1 | sed -e 's/^[^0-9]\+//;s/[()]//g'
echo -n "git: "; git --version | sed -e 's/^[^0-9]\+//'

