sumo-scan
=========

What the script does
--------------------

This script scans an existing EPICS support module directory tree and collects all
information necessary to generate a dependency database or *DB* file. The data
is formatted in `JSON <http://www.json.org>`_ format and printed to the
console. You can either save this output in a file or combine this script with
:doc`sumo-db <reference-sumo-db>` in a pipe to directly create a DB file.

The script takes one or mode commands and has a number of options. One
character options always start with a single dash "-", long options start with
a double dash "--" and commands are simple words on the command line.

Commands
--------

all
+++

This is the most important command. "all" combines the commands "deps", "repos"
and "groups". The output of the commands is combined in a single large `JSON
<http://www.json.org>`_ structure and printed to the console. 

deps
++++

This command collects dependencies from all "RELEASE" files and returns the
structure in `JSON <http://www.json.org>`_ format. Here is an example of the
returned data::

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

This command collects information about repositories and returns the structure
in `JSON <http://www.json.org>`_ format. Each directory is mapped to another
map. In this map the only key is the source type, e.g. "path" or "darcs". The
value is either, in case of "path" a string or, in case of "darcs" another map.
This map has the keys "url" for the darcs url of the repository and optionally
a "tag" key whose value is the darcs tag. Here is an example of the returned
data::

  {
     "repos": {
        "/srv/csr/Epics/R3.14.10/base/3-14-10-0-1": {
            "darcs": {
                "tag": "R3-14-10-0-1",
                "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/base/3-14-10"
            }
        },
        "/srv/csr/Epics/R3.14.12/base/3-14-12-2-1": {
            "darcs": {
                "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/base/3-14-12-2"
            }
        },
        "/srv/csr/Epics/R3.14.8/support/apps/wlsSupport/work": {
            "path": "rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.8/support/apps/wlsSupport/work"
        },
        "/srv/csr/Epics/R3.14.8/support/NewDyncon/3-0": {
            "darcs": {
                "tag": "R3-0",
                "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/support/dyncon"
            }
        },
        "/srv/csr/Epics/R3.14.8/support/NewDyncon/3-1": {
            "darcs": {
                "tag": "R3-1",
                "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/support/dyncon"
            }
        }
      }
  }

groups
++++++

This command collects modules of the same name but different versions in
groups. Here is an example of the returned data::

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

This command shows what module paths were found for module names. Here is an
example of the returned data::

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

This command shows module names were found module paths. Here is an example of
the returned data::

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

Options
-------

config
++++++

Option "-c" or "--config" must be followed by the name of a config file. If
this option is given, the program read the valued of the following options from
that file:

--dir, --info-file, --group-basedir, --exclude-path, --exclude-deps,
--source-patch, --darcs-dirtest, --accept-path, --missing-tag, --missing-repo,
--buildtag, --progress, --verbose

Command line options always have precedence over the value from the config file.

If a file named "sumo-scan.config" is found in the current directory, this file
is read if option "--config" doesn't specify a different filename. 

Currently it is not an error if the config file is not found.

make-config
+++++++++++

This option must be following by a filename or "-". The config file, if found,
is combined with the rest of the command line options and the result is written
to the given file or, if the filename was "-", to the console.

dir
+++

Option "-d" or "--dir" must be followed by a directory name. This specifies the
directory that is searched for the sources of EPICS support modules. You can
specify more than one directory by using this option more than once.

info-file
+++++++++

Option "-i" or "--info-file" must be followed by the name of a file that was
created in a previous run of the script. In this case the script doesn't scan
directories but simply reads data from the given file. This may be useful for
the name2paths or path2names command since scanning the support directories
again for these commands may take a long time.

group-basedir
+++++++++++++

Option "-g" or "--group-basedir" must be followed by a directory name. When a
support module is found in a directory path, the part from the start that
matches one of the given group-basedirs is cut off. The remaining string is
examined to get the modulename and the versionname. You can specify more than
one group base directory.

exclude-path
++++++++++++

Option "--exclude-path" must be followed by a regular expression. Paths that
match one of the given regular expressions are ignored. You can specify more
than one regular expression.

exclude-deps
++++++++++++

Option "--exclude-deps" must be followed by a regular expression. Modules where
at least one of the dependencies match the given regular expression are
ignored. 

source-patch
++++++++++++

Option "-P" or "--source-patch" must be followed by a patch expression. This is
a python tuple of two strings. The first one is a regular expression, the
second one is a replacement string according to the rules of the python regular
expression library (module "re"). The regular expression and the replacement
string are applied to all source urls. You can specify module than one regular
expression.

accept-path
+++++++++++

Option "--accept-path" must be followed by a path. For each module the program
tries to find the source repository. It also retrieves a list of all version
control tags. The newest tag is matched with the end of the path string. If
both match, the tag is stored in the source specification, otherwise the tag is
ignored. With this option you can specify paths of modules where the tag is
always taken, no matted what the path string is. You can specify more than one
accept path.

darcs-dirtest
+++++++++++++

If option "--darcs-dirtest" is given, the program checks if a directory
"_darcs" can be found at the location of the remote repository. If this
directory is not found, the repository is not put to the source specification
of the module.

missing-tag
+++++++++++

If this option is given, the program shows all modules where a source
repository but not tag was found.

missing-repo
++++++++++++

If this option is given, the program shows all modules where no source
repository was found.

buildtag
++++++++

Option "-t" or "--buildtag" must be followed by a buildtag. If this option is
given, the program scans only directories that match the given buildtag. This
is used to scan directory trees that were created by 
`sumo-build <reference-sumo-build>`.

progress
++++++++

If option "-p" or "--progress" is given, the program shows it's progress on
stderr.

verbose
+++++++

If "-v" or "--verbose" is given, the program shows all calls of external
programs on the console.

dry-run
+++++++

If "-n" or "--dry-run" is given, the program just shows what it *would* do.
