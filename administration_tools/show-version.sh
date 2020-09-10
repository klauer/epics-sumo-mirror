#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

if [ "$1" = "-h" ]; then
    echo "$ME : show the current sumo version."
    echo 
    echo "options:"
    echo "-h  : this help"
    echo "-b  : just show the pure version number"
    exit 0
fi

if [ "$1" = "-b" ]; then
    PYTHONPATH=.. python3 ../bin/sumo --version | sed -e 's/sumo *//'
else
    PYTHONPATH=.. python3 ../bin/sumo --version
fi
