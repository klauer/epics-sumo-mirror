#!/bin/sh

MYDIR=`pwd`

cd ..
. PATH.sh

# needed since sumo-scan call EPICS make:
EPICS_HOST_ARCH=`test/scripts/EpicsHostArch.pl`
export EPICS_HOST_ARCH

cd $MYDIR

SUPPORTDIR=/opt/Epics/R3.14.8/support
SCANFILE=R3-14-8-supports.SCAN
DBFILE=R3-14-8.DB

python2.5 `which sumo-scan` -c sumo-scan-3-14-8.config all > $SCANFILE

#python2.5 `which sumo-scan` -d $SUPPORTDIR --exclude-deps 'home/balzer|synApps' --exclude-paths 'synApps' -g $SUPPORTDIR -g /opt/Epics/R3.14.8 -g /opt/Epics/R3.14.10 -g /opt/Epics/R3.14.12 -d $SUPPORTDIR --darcs-dirtest -p all \
#  -P 'r"^([^:]*)$",r"rcsadm@aragon.acc.bessy.de:\1"' \
#  -P 'r"^([^@]*)$",r"rcsadm@\1"' \
#  -P 'r"\b(aragon)(?:|\.acc):",r"\1.acc.bessy.de:"' \
#  -P '":darcs-repos",":/opt/repositories/controls/darcs"' \
#  -P 'r"/srv/csr/(repositories/controls/darcs)",r"/opt/\1"' \
#  -P 'r"/srv/csr/Epics","/opt/Epics"' --make-config ""

#> $SCANFILE 

#perl -pi -e 's/aragon:/aragon.acc.bessy.de:/g' $SCANFILE
#perl -pi -e 's/aragon.acc:/aragon.acc.bessy.de:/g' $SCANFILE
#perl -pi -e 's#/srv/csr/repositories/controls/darcs#rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs#' $SCANFILE
#
#cat $SCANFILE| perl -ne 'if ($_=~/"path"/){$p=1;print;next;};if ($p) {$_=~s#/srv/csr/Epics#rscadm\@aragon.acc.bessy.de:/opt/Epics#;$p=0;};print;' > $SCANFILE.new
#
#rm $SCANFILE
#mv $SCANFILE.new $SCANFILE

python2.5 `which sumo-db` -c sumo-db-3-14-8.config convert stable $SCANFILE > $DBFILE
#  -P 'r"^/srv/csr/Epics",r"rcsadm@aragon.acc.bessy.de:/opt/Epics"' > $DBFILE
