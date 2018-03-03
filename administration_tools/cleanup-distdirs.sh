#!/bin/bash

ME=$(readlink -f "$0")
MYDIR=$(dirname "$ME")

cd "$MYDIR/.."

rm -rf dist
rm -rf dist-bitbucket

