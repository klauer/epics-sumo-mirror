#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")
SCRIPT=$(basename $ME)

cd "$MYDIR"
TOP=$(readlink -f "$MYDIR/../..")

source docker.config

set -e

function HELP {
    echo "$SCRIPT : run a docker container"
    echo
    echo "usage: $SCRIPT DOCKERFILE [OPTIONS]" 
    echo "where DOCKERFILE is one of the following:"
    ls $DOCKERFILEDIR
    echo
    echo "options:"
    echo "  -h  : display this help"
    echo "  --shell : do not build packages, just start a shell"
    echo "  --x11 : for --shell, start with x11 support"
    echo " -v --verbose : just show what the program would do"
    echo " -n --dry-run : just show what the program would do"
    exit 0
}

function CMD {
    # $1: command
    if [ -n "$VERBOSE" -o -n "$DRY_RUN" ]; then
        echo "$1"
    fi
    if [ -z "$DRY_RUN" ]; then
        bash -c "$1"
    fi
}

declare -a ARGS
START_SHELL=""
START_X11=""
VERBOSE=""
DRY_RUN=""

while true; do
    case "$1" in
        -h | --help )
            HELP;
            shift
            ;;
        --shell )
            START_SHELL="yes"
            shift
            ;;
        --x11 )
            START_X11="yes"
            shift
            ;;
        -n | --dry-run )
            DRY_RUN="yes"
            shift
            ;;
        -v | --verbose )
            VERBOSE="yes"
            shift
            ;;
    -- ) shift; break ;;
    * ) 
            if [ -z "$1" ]; then
                break;
            fi
            ARGS+=("$1")
            shift
            ;;
  esac
done

DOCKERFILE=${ARGS[0]}

if [ -z "$DOCKERFILE" ]; then
    echo "Error, dockerfile argument missing"
    exit 1
fi

if [ ! -e $DOCKERFILEDIR/$DOCKERFILE ]; then
    echo "Error, there is no DOCKERFILE named $DOCKERFILE"
    exit 1
fi

DIST=""
if grep -q '\<apt-get\>' $DOCKERFILEDIR/$DOCKERFILE; then 
    DIST="deb"
fi
if grep -q '\<rpm\>' $DOCKERFILEDIR/$DOCKERFILE; then 
    DIST="rpm"
fi

DOCKERIMAGE=$(imagename $DOCKERFILE)

# path to administration_tools inside the container:
DOCKER_TOOL_PATH="/root/$APPLICATION/administration_tools/docker"

dist_dir="$TOP/dist/$DOCKERFILE"

if [ ! -d "$dist_dir" ]; then
    mkdir -p "$dist_dir" && chmod 777 "$dist_dir"
fi

# create dependency file(s):
if [ -n "$(must_make administration_tools/DEPS.RPM setup.py)" ]; then
    cd ../..
    python3 setup.py deps-rpm > $MYDIR/DEPS.RPM
    python3 setup.py deps-deb > $MYDIR/DEPS.DEB
    cd $MYDIR
    # create the DEPS.* files if they were not created by setup.py:
    touch DEPS.RPM DEPS.DEB
fi

if [ -n "$START_SHELL" ]; then
    echo "------------------------------------------------------------"
    echo "Create packages:"
    echo
    echo "cd $DOCKER_TOOL_PATH && ./mk-$DIST.sh"
    echo
    echo "------------------------------------------------------------"
    echo "Test packages:"
    echo
    if [ $DIST = "deb" ]; then
        echo "dpkg -i /root/dist/[file]" 
    fi
    if [ $DIST = "rpm" ]; then
        echo "rpm -i /root/dist/[file]" 
    fi
    echo
fi

if [ -n "$START_SHELL" ]; then
    PROG="/bin/bash"
else
    PROG="$DOCKER_TOOL_PATH/mk-$DIST.sh"
fi

echo "---------------------------------------" >> $MYDIR/$RUN_LOGFILE
echo "$me $DOCKERFILE" >> $MYDIR/$RUN_LOGFILE

RM_OPT="--rm"
X11_OPTS=""
if [ -n "$START_X11" ]; then
    X11_OPTS="--env DISPLAY --volume ~/.Xauthority:/root/.Xauthority:Z --net=host"
fi

CMD "$DOCKER run $RM_OPT $X11_OPTS -t --volume $dist_dir:/root/dist --volume $TOP:/root/$APPLICATION -i $DOCKERIMAGE $PROG" 2>&1 | tee -a $MYDIR/$RUN_LOGFILE
