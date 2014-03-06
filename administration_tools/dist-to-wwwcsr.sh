#!/bin/sh

curr_ver=`grep '^my_version' ../setup.py | sed -e 's/^[^"]*//;s/"//g'`

rm -f ../dist/sumo.tar.gz
rm -f ../dist/sumo.zip
ln -s sumo-$curr_ver.tar.gz ../dist/sumo.tar.gz
ln -s sumo-$curr_ver.zip ../dist/sumo.zip

rsync -a -u ../dist/ wwwcsr@www-csr.bessy.de:/home/wwwcsr/www/control/sumo/sumo-dist/
