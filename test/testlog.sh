#!/bin/bash
LOGTMP="tests.tmp"
LOG="tests.log"

echo >> $LOGTMP
echo "=================================================" >> $LOGTMP
date -Iseconds >> $LOGTMP
echo "Tests ran successfully on this environment:" >> $LOGTMP
echo "-------------------------------------------------" >> $LOGTMP
./versions.sh >> $LOGTMP
echo "=================================================" >> $LOGTMP

cat $LOGTMP >> $LOG

./versions.sh

echo 
echo "created $LOGTMP"
echo "appended $LOG"
