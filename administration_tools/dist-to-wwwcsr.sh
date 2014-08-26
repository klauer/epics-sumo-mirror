#!/bin/sh

curr_ver=`grep '#VERSION#' ../setup.py | sed -e 's/^[^"]\+"\([^"]\+\).*$/\1/'`

rm -f ../dist/sumo.tar.gz
rm -f ../dist/sumo.zip
ln -s sumo-$curr_ver.tar.gz ../dist/sumo.tar.gz
ln -s sumo-$curr_ver.zip ../dist/sumo.zip

rsync -a -u ../dist/ wwwcsr@www-csr.bessy.de:/home/wwwcsr/www/control/sumo/sumo-dist/
