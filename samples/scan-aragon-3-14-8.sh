#!/bin/sh

SUPPORTDIR=/opt/Epics/R3.14.8/support
SCANFILE=R3-14-8-supports.SCAN
DBFILE=R3-14-8.DEPS

sumo-scan -c sumo-scan-3-14-8.config all > $SCANFILE

sumo-db -c sumo-db-3-14-8.config convert stable $SCANFILE > $DBFILE

cp $DBFILE DEPS.DB
