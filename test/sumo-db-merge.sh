#!/bin/bash

ME=`basename $0 .sh`

source settings.sh

echo -e "\n-> Test sumo db merge" >&2

rm -rf $EXAMPLEDIR
mkdir $EXAMPLEDIR
cd $EXAMPLEDIR > /dev/null

cp ../tmp-sumo-db-convert/DEPS.DB .

# modify DEPS.DB and create extra db file for merge test:
cp DEPS.DB DEPS.ORIG
mkdir extra
# prepare DEPS.DB in extra directory:
echo "{" > extra/DEPS.DB
# extract "SEQ" entry:
cat DEPS.DB  | sed -n -e '/^    "SEQ"/,/^    },/p' >> extra/DEPS.DB
# remove SEQ entry from DEPS.DB:
sed  -e '/^    "SEQ"/,/^    },/d' -i DEPS.DB
# extract MISC_DEBUGMSG:R3.0 from DEPS.DB:
cat DEPS.DB  | sed -n -e '/^    "MISC_DEBUGMSG"/,/^    },/p' >> extra/DEPS.DB
sed -e '$s/},/}/' -i extra/DEPS.DB
echo "}" >> extra/DEPS.DB
# now copy MISC_DEBUGMSG:R3-1 to MISC_DEBUGMSG:R3-2
$SUMO db -y --dbdir extra cloneversion MISC_DEBUGMSG R3-1 R3-2 >/dev/null

# add a make recipe to the new support:
$SUMO db -y --dbdir extra make-recipes MISC_DEBUGMSG:R3-2 all 'cd $DIR && ./configure --prefix=.' '$(MAKE) -C $DIR'
$SUMO db -y --dbdir extra make-recipes MISC_DEBUGMSG:R3-2 clean '$(MAKE) -C $DIR realclean'

# add extra RELEASE line to the new support:
$SUMO db -y --dbdir extra extra MISC_DEBUGMSG:R3-2 '# extra line 1' '# extra line 2'

# finally: do the merge:
$SUMO db --dbdir . merge extra/DEPS.DB

echo "DB backup file:"
cat DEPS.DB.bak | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"

echo "DB file:"
cat DEPS.DB | sed -e "s#$PWD_NICE##;s#$PWD_REAL##;s#\"[0-9a-f]\{12\}\"#\"ABCDABCDABCD\"#"

