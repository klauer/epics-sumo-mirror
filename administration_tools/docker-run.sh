#!/bin/bash

if [ -z "$1" -o "$1" = "-h" ]; then
    me=`basename $0`
    echo "$me : run a docker container"
    echo
    echo "usage: $me DOCKERFILE" 
    echo "where DOCKERFILE is one of the following:"
    ls docker
    exit 1
fi

DOCKERFILE="$1"

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

sumo=`pwd`

DOCKERIMAGE=hzb/sumo-builder-$DOCKERFILE

dist_dir="dist/$DOCKERFILE"

if [ ! -d "$dist_dir" ]; then
    mkdir -p "$dist_dir" && chmod 777 "$dist_dir"
fi

echo "------------------------------------------------------------"
echo "Create packages:"
echo
if [ $DIST = "deb" ]; then
    echo "cd /root/sumo/administration_tools && ./mk-deb.sh"
fi
if [ $DIST = "rpm" ]; then
    echo "cd /root/sumo/administration_tools && ./mk-rpm.sh"
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
docker run -t --volume $sumo/$dist_dir:/root/dist --volume $sumo:/root/sumo -i $DOCKERIMAGE /bin/bash

