#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo config show with a faulty config file." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

# copy sample config file
cat ../sumo-config-make-CONFIG.tmp | sed -e 's/preload/opt-preload/' > sumo.config.ok

# create various wrong versions of the file:
cat sumo.config.ok | sed -e 's/"\."/"./' > sumo.config.faulty-json
cat sumo.config.ok | sed -e 's/dbdir/DBDIR/' > sumo.config.wrong-key
cat sumo.config.ok | sed -e 's/"\."/[ "." ]/' > sumo.config.list-for-str
cat sumo.config.ok | sed '/dir-patch/,+2d;s/\("dbdir"\)/"dir-patch": "abc",\n    \1/' > sumo.config.str-for-list
cat sumo.config.ok | sed '/#opt-preload/,+2d;s/\("dbdir"\)/"#opt-preload": "abc",\n    \1/' > sumo.config.str-for-list2
cat sumo.config.ok | sed '/dir-patch/,+2d;s/\("dbdir"\)/"dir-patch": { "abc":1 },\n    \1/' > sumo.config.dict-for-list
cat sumo.config.ok | sed '/#opt-preload/,+2d;s/\("dbdir"\)/"#opt-preload": { "abc":1 },\n    \1/' > sumo.config.dict-for-list2

CFG_FILES="sumo.config.ok sumo.config.faulty-json sumo.config.wrong-key sumo.config.list-for-str sumo.config.str-for-list sumo.config.str-for-list2 sumo.config.dict-for-list sumo.config.dict-for-list2"

for file in $CFG_FILES; do
    echo "sumo config show on $file:"
    $SUMO --no-default-config -c $file config show 2>&1
    echo
done

