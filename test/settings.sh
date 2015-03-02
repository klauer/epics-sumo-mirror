# include file for test scripts

if [ -z "$1" ]; then
    PYTHON="python"
fi

BINDIR=`pwd`/../bin
SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

SUPPORTDIR=`(cd data/epics > /dev/null && pwd)`
REPODIR=`(cd data/repos > /dev/null && pwd)`
EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`
