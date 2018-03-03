#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR/../doc/_build/html"
echo "put *" | sftp -b - -r goetzpf@web.sourceforge.net:/home/project-web/epics-sumo/htdocs
