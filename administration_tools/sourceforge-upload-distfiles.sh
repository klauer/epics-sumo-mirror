cd ..
DESTHOST=goetzpf@frs.sourceforge.net
DESTPATH=/home/frs/project/epics-sumo
#scp dist/*.tar.gz $DESTHOST:$DESTPATH
#scp dist/*.zip $DESTHOST:$DESTPATH
scp -r dist/* $DESTHOST:$DESTPATH
scp README.sourceforge $DESTHOST:$DESTPATH
