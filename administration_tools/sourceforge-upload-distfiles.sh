cd ..
DESTHOST=goetzpf@frs.sourceforge.net
DESTPATH=/home/frs/project/epics-sumo
scp dist/*.tar.gz $DESTHOST:$DESTPATH
scp dist/*.zip $DESTHOST:$DESTPATH
scp README $DESTHOST:$DESTPATH
