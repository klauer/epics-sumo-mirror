#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok sumo-db-convert.tst"
        echo
        exit
fi

if [ -z "$1" ]; then
        PYTHON="python"
else
        PYTHON=$1
fi

PWD_NICE=`pwd`

echo -e "\n-> Test sumo db find" >&2

DEPS=tmp-sumo-db-convert/DEPS.DB

echo -e "find mcan:"
$PYTHON ../bin/sumo db --arch vxWorks-68040 --arch vxWorks-ppc603 --db $DEPS find mcan | sed -e s#$PWD_NICE##

echo -e "\nfind mcan -b:"
$PYTHON ../bin/sumo db --arch vxWorks-68040 --arch vxWorks-ppc603 --db $DEPS find mcan -b | sed -e s#$PWD_NICE##

echo -e "\nfind '^A' -b:"
$PYTHON ../bin/sumo db --arch vxWorks-68040 --arch vxWorks-ppc603 --db $DEPS find '^A' -b | sed -e s#$PWD_NICE##

