#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-db find" >&2

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
echo -e "find unstable mcan:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB find unstable mcan | sed -e "s/,$/, /g"

echo -e "\nfind unstable mcan -b:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB find unstable mcan -b

echo -e "\nfind unstable mcan.*patch -b:"
$PYTHON ../bin/sumo-db --arch vxWorks-68040 --arch vxWorks-ppc603 --db samples/DB find unstable mcan.*patch -b

