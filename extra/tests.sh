python2.5 pysupport.py --make-json -p --parse-release /opt/Epics/R3.14.8/support > XX
python2.5 pysupport.py --read-json X --make-json -p --calc-distribution '$SUPPORT/mcan/base-3-14-8 $SUPPORT/alarm/base-3-14 $SUPPORT/bspDep/cpuBoardInit $SUPPORT/bspDep/timer /opt/Epics/R3.14.8/support/genSub/1-6a'

python2.5 pysupport.py --read-json X --list-supports --json

python2.5 pysupport.py --json --read-json X --calc-distribution-by-file LIST2

