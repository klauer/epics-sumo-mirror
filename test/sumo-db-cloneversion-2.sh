#!/bin/bash

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

source settings.sh

echo -e "\n-> Test sumo db cloneversion." >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

$SUMO db --dbdir . -y cloneversion ALARM R3-7 R3-8-1 darcs '*' R3-8-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir . -y cloneversion ALARM R3-7 R3-10 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
$SUMO db --dbdir . -y cloneversion APPS_GENERICTEMPLATE PATH-3-0 R3-1 darcs /myrepo/apps/generictemplate R3-1 | sed -e "s#$PWD_REAL##;s#$PWD_NICE##"
echo "DB file:"
cat DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
 
