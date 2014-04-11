#!/bin/sh

SUPPORTDIR=/opt/Epics/R3.14.12/support
SCANFILE=R3-14-12.SCAN
DBFILE=R3-14-12.DB

python2.5 `which sumo-scan` -c sumo-scan-3-14-12.config all > $SCANFILE

python2.5 `which sumo-db` -c sumo-db-3-14-12.config convert stable $SCANFILE > $DBFILE

