#!/bin/sh
cd ../doc/_build/html
echo "put *" | sftp -b - -r goetzpf@web.sourceforge.net:/home/project-web/epics-sumo/htdocs
