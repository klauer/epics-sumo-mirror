#!/bin/sh

# creates the sample support directory tree.

if [ ! -e base ]; then
        echo "unpacking sample sources..."
        . ./sources.shar >/dev/null
fi

