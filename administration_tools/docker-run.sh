#!/bin/bash

if [ -z "$1" ]; then
    me=`basename $0`
    echo "$me : run a docker container"
    echo
    echo "usage: $me DOCKERFILE" 
    echo "where DOCKERFILE is one of the following:"
    ls docker
    exit 1
fi

DOCKERFILE="$1"

cd ..

sumo=`pwd`

DOCKERIMAGE=hzb/sumo-builder-$DOCKERFILE

dist_dir="dist/$DOCKERFILE"

if [ ! -d "$dist_dir" ]; then
    mkdir -p "$dist_dir" && chmod 777 "$dist_dir"
fi

echo "after docker is running you may want to:"
echo "cd /root/sumo/administration_tools && ./mk-deb.sh"
echo "   -or-"
echo "cd /root/sumo/administration_tools && ./mk-rpm.sh"
echo
docker run -t --volume $sumo/$dist_dir:/root/dist --volume $sumo:/root/sumo -i $DOCKERIMAGE /bin/bash

