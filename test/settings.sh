# include file for test scripts

# set PYTHON only if it is not yet defined:
if [ -z "$PYTHON" ]; then
    PYTHON="python3"
fi

# extend PYTHONPATH in order to find Sumo modules:
PYTHONPATH=`pwd`/..:$PYTHONPATH
export PYTHONPATH

# set the BINDIR:
BINDIR=`pwd`/../bin

SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

SUPPORTDIR=`(cd data/epics > /dev/null && pwd)`
REPODIR=`(cd data/repos > /dev/null && pwd)`
EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`
