#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR"

LOGFILE="DOCKER-RUN.LOG"

APPLICATION=sumo

set -e

function HELP {
    me=`basename $0`
    echo "$me : run a docker container"
    echo
    echo "usage: $me DOCKERFILE [OPTIONS]" 
    echo "where DOCKERFILE is one of the following:"
    ls docker
    echo
    echo "options:"
    echo "  -h  : display this help"
    echo "  --shell : do not build packages, just start a shell"
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

if [ ! -e docker/$DOCKERFILE ]; then
    echo "Error, there is no DOCKERFILE named $DOCKERFILE"
    exit 1
fi

DIST=""
if grep -q '\<apt-get\>' docker/$DOCKERFILE; then 
    DIST="deb"
fi
if grep -q '\<rpm\>' docker/$DOCKERFILE; then 
    DIST="rpm"
fi

cd ..

top=`pwd`

DOCKERIMAGE=hzb/$APPLICATION-builder-$DOCKERFILE

# path to administration_tools inside the container:
ADMIN_TOOL_PATH="/root/$APPLICATION/administration_tools"

dist_dir="dist/$DOCKERFILE"

if [ ! -d "$dist_dir" ]; then
    mkdir -p "$dist_dir" && chmod 777 "$dist_dir"
fi

if [ -n "$START_SHELL" ]; then
    echo "------------------------------------------------------------"
    echo "Create packages:"
    echo
    if [ $DIST = "deb" ]; then
        echo "cd $ADMIN_TOOL_PATH && ./mk-$DIST.sh"
    fi
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
    PROG="$ADMIN_TOOL_PATH/mk-$DIST.sh"
fi

echo "---------------------------------------" >> $MYDIR/$LOGFILE
echo "$me $DOCKERFILE" >> $MYDIR/$LOGFILE

CMD "docker run -t --volume $top/$dist_dir:/root/dist --volume $top:/root/$APPLICATION -i $DOCKERIMAGE $PROG" 2>&1 | tee -a $MYDIR/$LOGFILE
