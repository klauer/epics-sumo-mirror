#!/bin/sh

SUPPORTDIR=/opt/Epics/R3.14.8/support
SCANFILE=R3-14-8.SCAN
DBFILE=R3-14-8.DB

python2.5 `which sumo-scan` -c sumo-scan-3-14-8.config all > $SCANFILE

python2.5 `which sumo-db` -c sumo-db-3-14-8.config convert stable $SCANFILE > $DBFILE

