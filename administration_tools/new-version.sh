#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

# abort on errors:
set -e

cd "$MYDIR"

if [ -z "$1" ]; then
    echo "usage: $0 <version-string>"
    echo "patches the version strings in all parts of the project"
    exit 0
fi

VERSION="$1"

FILES="`ls ../python2/bin/*` `ls ../python3/bin/*` `ls ../python2/sumolib/[A-Za-z]*.py` `ls ../python3/sumolib/[A-Za-z]*.py` ../doc/conf.py ../setup.py"

for f in $FILES; do
    sed -i -e "s/\"[^\"]\+\" \+\(#VERSION#\)/\"$VERSION\" \1/" $f
done

hg qnew new-version-$VERSION -m "The version was changed to $VERSION."

