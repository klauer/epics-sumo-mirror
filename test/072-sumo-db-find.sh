#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$@

echo -e "\n-> Test sumo-db find" >&2

echo -e "find unstable mcan:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB --maxstate unstable find mcan 

echo -e "\nfind unstable mcan -b:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB --maxstate unstable find mcan -b

echo -e "\nfind unstable mcan.*patch -b:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB --maxstate unstable find mcan.*patch -b

