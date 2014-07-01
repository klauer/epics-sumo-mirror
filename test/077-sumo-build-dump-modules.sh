#!/bin/sh

ME=`basename $0 .sh`

if [ "$1" = "deps" ]; then
        echo "$ME.tst: $ME.sh $ME.out $ME.ok"
        echo
        exit
fi

PYTHON=$1

echo -e "\n-> Test sumo-build try --dump-modules" >&2

echo "Take modulespecs from samples/IDCP.CONFIG:"
$PYTHON ../bin/sumo-build --db samples/DB --maxstate stable --builddb samples/BUILDS --dump-modules try :load:samples/IDCP.CONFIG
echo "Take modulespecs from build 002:"
$PYTHON ../bin/sumo-build --db samples/DB --maxstate stable --builddb samples/BUILDS --dump-modules try :build:002 
echo "The same but remove SOFT:R2-5:"
$PYTHON ../bin/sumo-build --db samples/DB --maxstate stable --builddb samples/BUILDS --dump-modules try :build:002 :rm:SOFT:R2-5
echo "The same but remove change SOFT:R2-5 to SOFT:R2-6"
$PYTHON ../bin/sumo-build --db samples/DB --maxstate stable --builddb samples/BUILDS --dump-modules try :build:002 SOFT:R2-6
echo "The same but remove all and add SOFT:R2-7"
$PYTHON ../bin/sumo-build --db samples/DB --maxstate stable --builddb samples/BUILDS --dump-modules try :build:002 :clear SOFT:R2-7





