# include file for test scripts

if [ $PYVER != 2 -a $PYVER != 3 ]; then 
    echo "error, PYVER must be set to 2 or 3"
    exit
fi

# set PYTHON only if it is not yet defined:
if [ -z "$PYTHON" ]; then
    PYTHON="python$PYVER"
fi

# extend PYTHONPATH in order to find Sumo modules:
PYTHONPATH=`pwd`/../python$PYVER:$PYTHONPATH
export PYTHONPATH

# set the BINDIR:
BINDIR=`pwd`/../python$PYVER/bin

SUMO_SCAN="$PYTHON $BINDIR/sumo-scan -C"
SUMO="$PYTHON $BINDIR/sumo -C"

SUPPORTDIR=`(cd data/epics > /dev/null && pwd)`
REPODIR=`(cd data/repos > /dev/null && pwd)`
EXAMPLEDIR=tmp-$ME

PWD_NICE=`pwd`
PWD_REAL=`pwd -P`
