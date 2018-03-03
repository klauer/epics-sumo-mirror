#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

set -e

cd "$MYDIR/.."

for f in python3/bin/*; do
        echo "2to3 -w -n -f all -f idioms $f"
done

for f in python3/sumolib/*.py; do
        echo "2to3 -w -n -f all -f idioms $f"
done

echo "2to3 -w -n -f all -f idioms ../setup.py > ../setup-3.py"
