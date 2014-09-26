#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok 020-sumo db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`

echo -e "\n-> Test sumo db cloneversion." >&2

cp tmp-020-sumo-db-convert/DEPS.DB $ME-DEPS.tmp

$PYTHON ../bin/sumo db --db $ME-DEPS.tmp -y cloneversion ALARM R3-7 R3-8-1 darcs '*' R3-8-1 | sed -e s#$PWD_NICE##
$PYTHON ../bin/sumo db --db $ME-DEPS.tmp -y cloneversion ALARM R3-7 R3-10 | sed -e s#$PWD_NICE##
$PYTHON ../bin/sumo db --db $ME-DEPS.tmp -y cloneversion APPS_GENERICTEMPLATE PATH-3-0 R3-1 darcs /myrepo/apps/generictemplate R3-1 | sed -e s#$PWD_NICE##
echo "DB file:"
cat $ME-DEPS.tmp | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"
 
