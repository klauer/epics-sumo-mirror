#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db make-recipes" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

$SUMO db -y --dbdir . make-recipes ALARM:R3-7 all 'cd $DIR && ./configure --prefix=.' '$(MAKE) -C $DIR'
$SUMO db -y --dbdir . make-recipes ALARM:R3-7 clean '$(MAKE) -C $DIR realclean'
$SUMO db -y --dbdir . make-recipes MISC_DEBUGMSG:R3-0 
echo "DB file:"
cat DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"



