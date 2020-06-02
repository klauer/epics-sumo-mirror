#!/bin/bash
LOG="tests.log"

echo >> $LOG
echo "=================================================" >> $LOG
date -Iseconds >> $LOG
echo "Tests ran successfully on this environment:" >> $LOG
echo "-------------------------------------------------" >> $LOG
./versions.sh >> $LOG
echo "=================================================" >> $LOG

./versions.sh
