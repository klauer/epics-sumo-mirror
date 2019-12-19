#!/bin/bash

set -e

SCRIPT_FULL_NAME=$(readlink -e $0)
MYDIR=$(dirname $SCRIPT_FULL_NAME)
MYNAME=$(basename $SCRIPT_FULL_NAME)

BITBUCKET_TEMP_DIR=bitbucket-tmp
BITBUCKET_HTML_REPO="ssh://goetzpf@bitbucket.org/goetzpf/goetzpf.bitbucket.io"

cd "$MYDIR"

mkdir -p "$BITBUCKET_TEMP_DIR"
cd "$BITBUCKET_TEMP_DIR"
HTML_DIR=$(basename "$BITBUCKET_HTML_REPO")
if [ ! -d "$HTML_DIR" ]; then
    hg clone "$BITBUCKET_HTML_REPO"
else
    hg pull -u "$BITBUCKET_HTML_REPO" -R "$HTML_DIR"
fi

cp -a $MYDIR/../doc/_build/html/* "$HTML_DIR/sumo"
mv "$HTML_DIR/sumo/index.html" "$HTML_DIR/sumo/index-orig.html" 
cp -a $MYDIR/../doc/redirect.html "$HTML_DIR/sumo/index.html"
hg -R "$HTML_DIR" commit
hg -R "$HTML_DIR" push


