#!/bin/sh

PYTHON=$1

echo -e "\n-> Test sumo-db showall" >&2

# sed is used to add spaces after each "," at the end of the line. The old JSON
# library for python 2.5 doesn't do this.
$PYTHON ../bin/sumo-db --db samples/DB showall stable ALARM | sed -e "s/,$/, /g"


