sumo-scan
=========

What the script does
--------------------

This script scans an existing EPICS support module tree and collects all
information necessary to generate a dependency database or *DB* file. The data
is formatted in `JSON <http://www.json.org>`_ format and printed on the
console. You can either save this output in a file or combine this script with
:doc`sumo-db <reference-sumo-db>` in a pipe to directly create a DB file.

The script takes one or mode commands and has a number of options. Options
always start with a dash "-", commands are simple words.

Commands
--------

all
+++

For common applications this is the most important command. "all" combines the
commands "deps", "repos" and "groups". The output of the commands is combined
in a single large `JSON <http://www.json.org>`_ structure and printed to the
console. 

deps
++++

Collect dependencies from all "RELEASE" files and return the structure in 
`JSON <http://www.json.org>`_ format. Here is an example of the returned data::

  {
      "dependencies": {
          "/srv/csr/Epics/R3.14.8/support/alarm/3-3": {
              "EPICS_BASE": "/srv/csr/Epics/R3.14.8/base/3-14-8-2-0",
              "MISC": "/srv/csr/Epics/R3.14.8/support/misc/2-4",
              "TIMER": "/srv/csr/Epics/R3.14.8/support/bspDep/timer/4-0"
          },
          "/srv/csr/Epics/R3.14.8/support/alarm/3-4": {
              "EPICS_BASE": "/srv/csr/Epics/R3.14.8/base/3-14-8-2-0",
              "MISC": "/srv/csr/Epics/R3.14.8/support/misc/2-4",
              "TIMER": "/srv/csr/Epics/R3.14.8/support/bspDep/timer/5-0"
          },
          "/srv/csr/Epics/R3.14.8/support/csm/3-2": {
              "EPICS_BASE": "/srv/csr/Epics/R3.14.8/base/3-14-8-2-0"
          },
          "/srv/csr/Epics/R3.14.8/support/csm/3-3": {
              "EPICS_BASE": "/srv/csr/Epics/R3.14.8/base/3-14-8-2-0"
          },
      }
  }

repos
+++++

Collect information about repositories and return the structure in 
`JSON <http://www.json.org>`_ format. Each directory is mapped to a list of 2
or 3 items. The first item is the source or repository type, e.g. "path" or
"darcs". The second one is a path or repository URL and the third, optional
value is a repository tag. Here is an example of the returned data::

  {
     "repos": {
          "/srv/csr/Epics/R3.14.10/base/3-14-10-0-1": [
              "darcs",
              "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/base/3-14-10",
              "R3-14-10-0-1"
          ],
          "/srv/csr/Epics/R3.14.12/base/3-14-12-2-1": [
              "darcs",
              "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/base/3-14-12-2"
          ],
          "/srv/csr/Epics/R3.14.8/support/NewDyncon/3-0": [
              "darcs",
              "rcsadm@aragon.acc.bessy.de:/opt/csr/repositories/controls/darcs/epics/support/dyncon",
              "R3-0"
          ],
          "/srv/csr/Epics/R3.14.8/support/NewDyncon/3-1": [
              "darcs",
              "rcsadm@aragon.acc.bessy.de:/opt/csr/repositories/controls/darcs/epics/support/dyncon",
              "R3-1"
          ],
      }
  }

groups
++++++

Collect modules of the same name but different versions in groups. Here is
an example of the returned data::

  {
      "groups": {
          "AGILENT": {
              "/srv/csr/Epics/R3.14.8/support/agilent": [
                  "2-0",
                  "2-1",
                  "2-2",
                  "head"
              ]
          },
          "ALARM": {
              "/srv/csr/Epics/R3.14.8/support/alarm": [
                  "3-0",
                  "3-1",
                  "3-2",
                  "3-3",
                  "3-4",
                  "3-5",
                  "base-3-14"
              ]
          },
      }
  }

name2paths
++++++++++

Show what module paths were found for module names. Here is an example of the
returned data::

  {
      "name2paths": {
          "ALARM": [
              "/srv/csr/Epics/R3.14.8/support/alarm/3-2",
              "/srv/csr/Epics/R3.14.8/support/alarm/3-3",
              "/srv/csr/Epics/R3.14.8/support/alarm/3-5"
          ],
          "MOTOR": [
              "/srv/csr/Epics/R3.14.8/support/motor/6-4-4-1",
              "/srv/csr/Epics/R3.14.8/support/motor/6-5-1",
              "/srv/csr/Epics/R3.14.8/support/motor/6-5-2",
              "/srv/csr/Epics/R3.14.8/support/synApps/5-1-1-0/support/motor/5-9",
              "/srv/csr/Epics/R3.14.8/support/synApps/5-2-0-1/support/motor/6-1",
              "/srv/csr/Epics/R3.14.8/support/synApps/5-2-0/support/motor/6-1",
              "/srv/csr/Epics/R3.14.8/support/synApps/5-4-1/support/motor/6-4-3",
          ],
      }
  }

path2names
++++++++++

Show what module names were found module paths. Here is an example of the
returned data::

  {
      "path2names": {
          "/srv/csr/Epics/R3.14.8/support/alarm/3-0": [
              "ALARM"
          ],
          "/srv/csr/Epics/R3.14.8/support/alarm/3-1": [
              "ALARM"
          ],
          "/srv/csr/Epics/R3.14.8/support/alarm/3-2": [
              "ALARM"
          ],
          "/srv/csr/Epics/R3.14.8/support/synApps/5-2-0-1/support/genSub/1-6a": [
              "GENSUB",
              "GEN_SUB"
          ],
      }
  }
