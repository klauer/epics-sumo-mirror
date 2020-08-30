#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo build try" >&2

DEPSDIR=tmp-sumo-db-convert
SUPPORTDIR=tmp-sumo-build-new-0

echo -e "\n----------------------------"
echo -e "try with modules missing, detail 0:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR try ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC 

echo -e "\n----------------------------"
echo -e "try with modules missing, detail 1:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 1 try ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC 

echo -e "\n----------------------------"
echo -e "try with modules missing, detail 2:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 2 try ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC 

echo -e "\n----------------------------"
echo -e "try with modules missing, detail 3:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 3 try ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC 

echo -e "\n----------------------------"
echo -e "\ntry with complete modulelist, detail 0:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR try BASE ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC MISC_DEBUGMSG SOFT_DEVHWCLIENT

echo -e "\n----------------------------"
echo -e "\ntry with complete modulelist, detail 1:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 1 try BASE ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC MISC_DEBUGMSG SOFT_DEVHWCLIENT

echo -e "\n----------------------------"
echo -e "\ntry with complete modulelist, detail 2:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 2 try BASE ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC MISC_DEBUGMSG SOFT_DEVHWCLIENT

echo -e "\n----------------------------"
echo -e "\ntry with complete modulelist, detail 3:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 3 try BASE ALARM:R3-8-modified MCAN BSPDEP_TIMER BSPDEP_VMETAS MISC_DBC MISC_DEBUGMSG SOFT_DEVHWCLIENT

echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist, detail 0:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:TAGLESS-2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0

echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist, detail 1:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 1 try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:TAGLESS-2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0

echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist, detail 2:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 2 try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:TAGLESS-2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0

echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist, detail 3:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 3 try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:TAGLESS-2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0

# Note: the following test does not really test that "-X stable" works since
# this doesn' filter builds if there is only one. This just tests that option
# "-X" is accepted and that a given string is internally compiled to a regular
# expression.
echo -e "\n----------------------------"
echo -e "\ntry with completely versioned modulelist, only stable builds, detail 3:\n"
$SUMO build --dbdir $DEPSDIR --builddir $SUPPORTDIR --detail 3 -X stable try BASE:R3-14-12-2-1 ALARM:R3-8-modified MCAN:TAGLESS-2-6-1 BSPDEP_TIMER:R6-2 BSPDEP_VMETAS:TAGLESS-2-1-modified MISC_DBC:PATH-3-0 MISC_DEBUGMSG:R3-0 SOFT_DEVHWCLIENT:TAR-3-0
