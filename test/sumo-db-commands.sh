#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db commands" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

$SUMO db -y --dbdir . commands ALARM:R3-7 'echo "This is a" > text.txt' 'echo "simple text" >> text.txt'
echo "DB file:"
cat DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"



