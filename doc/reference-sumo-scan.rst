sumo-scan
=========

What the script does
--------------------

This script scans an existing EPICS support module directory tree and collects all
information necessary to generate a dependency database or *DB* file. The data
is formatted in `JSON <http://www.json.org>`_ format and printed to the
console. You can either save this output in a file or combine this script with
:doc:`sumo-db <reference-sumo-db>` in a pipe to directly create a DB file.

The script takes one or mode commands and has a number of options. Single
character options always start with a single dash "-", long options start with
a double dash "--", commands are simple words on the command line.

How it works
------------

The program collects information in several phases. The output of each phase is
taken as an input for the next phase. If you use the command "all", the first
three phases are run at a time. If you run some phases alone by using the
commands "deps", "groups" or "repos" you have to provide the input of a phase
from a file by using the command line option "--info-file".

All three phases that are needed to create the data for generating a dependency
database with :doc:`sumo-db <reference-sumo-db>` are combined with the command
"all". 

Two other phases "name2paths" and "path2names" are implemented to get
information on the existing module support tree but are not needed to create a
dependency database.

Phase I, RELEASE file scanning
++++++++++++++++++++++++++++++

Information on dependencies of EPICS modules is stored in files named "RELEASE"
in directory "configure". For each module the module depends on, there is a
variable with a path. This is a short example of what you could find in a
RELEASE file::

  SUPPORT=/opt/Epics/R3.14.8/support
  MISC=$(SUPPORT)/misc/2-4
  ALARM=$(SUPPORT)/alarm/3-1
  SOFT=$(SUPPORT)/soft/2-2

The script calls the "make" program for each "RELEASE" file found and lets make
report a list of all generated variables. By calling make it is ensured that
all macros, e.g. "SUPPORT" in the example above, are resolved. By calling
"make" twice, one time without and one time with the "RELEASE" file we can
calculate a difference of the set of defined variables of both runs. This
difference contains all the changes in variables that are caused by parsing the
"RELEASE" file.

From this set of variable names and values the script removes names which match
a given list. For example, "TOP" usually refers to a directory that is not an
EPICS support.

The remaining variable definitions are assumed to be module dependencies. 

The program builds a map where the keys are absolute paths of support modules.
The values are maps which map variable names to absolute paths which are in
fact the module's dependencies. Here is a short `JSON <http://www.json.org>`_
example of the created data structure::

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

Phase II, Grouping
++++++++++++++++++

In this phase the program tries to build groups of modules. A group is a
collection all the versions of a support module. This is done by parsing module
paths. The program assumes that each module has a path of the form
"[BASEDIR]/[MODULEPATH]/[VERSION]". [VERSION] is simply the last part of the
path that contains no slashes "/". [BASEDIR] is given as a command line option
to the program (see `group-basedir`_) and [MODULEPATH] is all that remains of
the path. In order to create a *modulename* the program changes all characters
in [MODULEPATH] to uppercase and replaces all slashes "/" with underscore "_"
characters. Here is an example of the created datastructure in 
`JSON <http://www.json.org>`_ format::

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

Phase III, repository scan
++++++++++++++++++++++++++

Usually your support modules are managed by a version control system. Currently
the program only supports *darcs* but in the near future support for mercurial
and git will be added. 

In each module the program looks for the data of a supported version control
system. If no version control data is found, the program marks the source of
the module as a *path* meaning that `sumo-build <reference-sumo-build>` will
copy the sources from exactly that path.

If version control data is found the program it looks for a repository tag. It
only accepts a tag if it matches the last part of the support module path. The
program creates a version number from both, the path and the tag and only if
this number is equal, the tag is accepted. Here are some examples:

============================    =======   ============
path                            tag       tag accepted
============================    =======   ============
/Epics/support/NewDyncon/3-1    R3-1      yes
/Epics/support/NewDyncon/3-0    ver-3-0   yes
/Epics/support/NewDyncon/2-9    R2-8      no
/Epics/support/NewDyncon/2-7    R2-8      no
============================    =======   ============

The program also looks for the path of the foreign repository, this is assumed
to be the central repository we should refer to. If this is not found, the
program takes the path of the working copy as the source repository. In this
case, any version tag is ignored.

Here is an example of the generated data
in `JSON <http://www.json.org>`_ format::

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

Optional 

Optional Phase IV, name to paths map
++++++++++++++++++++++++++++++++++++

This optional phase that is started with the command "name2paths" creates a map
that shows what paths were found for modules. Here is an example of the created
datastructure in `JSON <http://www.json.org>`_ format::

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

Optional Phase V, paths to names map
++++++++++++++++++++++++++++++++++++

This optional phase that is started with the command "path2names" creates a map
that shows what module names were used for what module paths. Here is an
example of the created datastructure in `JSON <http://www.json.org>`_ format::

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

Program output
++++++++++++++

The output of all phases that are run is combined in a single 
`JSON <http://www.json.org>`_ datastructure that is printed on the console.

From the paths of each RELEASE file, a module name is constructed. Each path of
a support module from a RELEASE is added to the list of dependencies of that
module.

Since all the consecutive calls of "make" may take some time, the results of
the RELEASE file scan can be saved as a file and used later on with other
commands like "path2names" or "groups". This is the meaning of the "-i" or
"--info-file" option.

Commands
--------

This is a list of all commands:

makeconfig {FILE}
+++++++++++++++++

Create a new configuration file from the given options. If the filename is '-'
dump to the console, if it is omitted, rewrite the configuration file that was
read before (see option --config).

all
+++

This is the most important command. "all" combines the commands "deps",
"groups" and "repos". The output of the commands is combined in a single large
`JSON <http://www.json.org>`_ structure and printed to the console. You can use
the output of this command as input for :doc:`sumo-db <reference-sumo-db>` in
order to create a dependency database.

deps
++++

This command collects dependencies from all "RELEASE" files and returns the
structure in `JSON <http://www.json.org>`_ format. For details see 
`Phase I, RELEASE file scanning`_.

groups
++++++

This command collects modules of the same name but of different versions in
groups. For details see `Phase II, Grouping`_.

repos
+++++

This command collects information about repositories and returns the structure
in `JSON <http://www.json.org>`_ format. For details see 
`Phase III, repository scan`_.

name2paths
++++++++++

This command shows what module paths were found for module names. You do not
need this command in order to generate a dependency database. For details see
`Optional Phase IV, name to paths map`_.


path2names
++++++++++

This command shows what module names were used for what module paths. You do not
need this command in order to generate a dependency database. For details see
`Optional Phase V, paths to names map`_.

Options
-------

summary
+++++++

With this option the program prints a one line summary of it's function.

doc
+++

With this option the program shows a link to the sumo documentation on the HZB
web server.

test
++++

With this option the program performs a simple self test.

config
++++++

This option, that can be given as "-c" or "--config". It must be followed by the name of a configuration file. If this option it is used the values of some of the command line options are taken from this file. If an option given on the command line specifies a value different from the value of the configuration file, the value from the command line takes precedence. The configuration has `JSON <http://www.json.org>`_ format. The file contains a map where the keys are the long names of the options. Here is an example::

  {
      "darcs_dirtest": true,
      "dir": [
          "/opt/csr/Epics/R3.14.12/base/3-14-12-2-1",
          "/opt/Epics/R3.14.12/support"
      ],
      "exclude_deps": "home/",
      "exclude_path": [
          "apps/crateCtrl/XXXXX",
          "busy/vendor",
          "monoapps",
          "std/vendor",
          "devIocStats/vendor"
      ],
      "group_basedir": [
          "/opt/Epics/R3.14.12/support",
          "/opt/Epics/R3.14.12"
      ],
      "hint": [
      ],
      "ignore_name": [
          "TOP",
          "EPICS_SUPPORT",
          "SUPPORT",
          "TEMPLATE_TOP",
          "EPICS_SITE_TOP",
          "EPICS_MODULES",
          "MSI"
      ],
      "missing_repo": null,
      "missing_tag": null,
      "progress": true,
      "source_patch": [
          "r\"^([^:]*)$\",r\"rcsadm@aragon.acc.bessy.de:\\1\"",
          "r\"^([^@]*)$\",r\"rcsadm@\\1\"",
          "r\"\\b(aragon)(?:|\\.acc):\",r\"\\1.acc.bessy.de:\"",
          "r\"^rcsadm@localhost:\",r\"rcsadm@aragon.acc.bessy.de:\"",
          "\":darcs-repos\",\":/opt/repositories/controls/darcs\"",
          "r\"/(srv|opt)/csr/(repositories/controls/darcs)\",r\"/opt/\\2\"",
          "r\"/srv/csr/Epics\",\"/opt/Epics\""
      ],
      "verbose": null
  }

The following options are stored in the configuration file:

- darcs_dirtest
- dir
- exclude_deps
- exclude_path
- group_basedir
- hint
- ignore_name
- missing_repo
- missing_tag
- progress
- source_patch
- verbose

If a file named "sumo-scan.config" is found in the current working directory,
this file is read if option "--config" is not used to specify a different file.

In the current implementation it is not an error if the specified configuration
file is not found.

dir
+++

Option "-d" or "--dir" must be followed by a directory name. This specifies the
directory that is searched for the sources of EPICS support modules. You can
specify more than one directory by using this option more than once. The value
of this options is stored in the configuration file.

info-file
+++++++++

Option "-i" or "--info-file" must be followed by the name of a file that was
created in a previous run of the script. In this case the script doesn't scan
directories but simply reads `JSON <http://www.json.org>`_ data from the given
file. This may be useful for commands like "name2paths" or "path2names" command
since scanning the support directories again for these commands may take a long
time.

ignore-name
+++++++++++

Option "-N" or "--ignore-name" must be followed by a string. This string
defines a variable name that should be ignored when it is found in an RELEASE
file. You can use this option several times in order to defined more than one
variable name. The value of this option is stored in the configuration file.

group-basedir
+++++++++++++

Option "-g" or "--group-basedir" must be followed by a directory name. It
defines the part of the directory path that is the same for all support
modules. This is needed in order to generate a module name from the module's
directory path. You can use this option several times in order to defined more
than one base directory. The value of this option is stored in the
configuration file.

exclude-path
++++++++++++

Option "--exclude-path" must be followed by a regular expression. Support
module paths that match one of the given regular expressions are ignored. You
can use this option several times in order to defined more than one regular
expression. The value of this option is stored in the configuration file.

exclude-deps
++++++++++++

Option "--exclude-deps" must be followed by a regular expression. Modules where
at least one of the dependencies match the given regular expression are
ignored. The value of this option is stored in the configuration file.

source-patch
++++++++++++

Option "-P" or "--source-patch" must be followed by a patch expression. This is
a python tuple of two strings, meaning that both strings must be separated by a
comma. The first string is a regular expression, the second one is a
replacement string according to the rules of the python regular expression
library (module "re"). The regular expression and the replacement string are
applied to all source urls. You can specify module than one regular expression.
Here is an example::

  -P 'r"\b(aragon)(?:|\.acc):",r"\1.acc.bessy.de:"'

For python regular expressions see
`<http://docs.python.org/2/library/re.html>`_.

The value of this option is stored in the configuration file.

hint
++++

This option must be followed by a string. It specifies an additional hint for
the support module scanner. The string, also called *hint*, must be a regular
expression followed by a comma ',' and a list of comma separated flags. A
*flag* is string from a list of known flags. The known flags are "PATH" and
"TAGLESS". If the flag is "PATH" the support module's source is set to "path"
meaning that repository information is ignored and the source of the module is
just the path of the installed support module. If the flag is "TAGLESS", the
version control tag is ignored and the module's source is set to the local
repository where the module is installed.  The value of this option is stored
in the configuration file.

darcs-dirtest
+++++++++++++

If this option is given the program tests if the default darcs repository
exists and if it contains a "_darcs" directory. If the remote directory is not
found, the module's source is treated as if "TAGLESS" was given with option
"--hint".  The value of this option is stored in the configuration file.

missing-tag
+++++++++++

If this option is given the program shows all directories where a repository
was found but no tag was found.  The value of this option is stored in the
configuration file.

missing-repo
++++++++++++

If this option is given the program shows all directories no repository was
found. The value of this option is stored in the configuration file.

buildtag
++++++++

Option "-t" or "--buildtag" must be followed by a *buildtag*. If this option is
given, the program scans only directories that match the given buildtag. This
feature is used to scan parts of a support directory that was created by
`sumo-build <reference-sumo-build>`.

progress
++++++++

If option "-p" or "--progress" is given, the program shows it's progress on
stderr. The value of this option is stored in the configuration file.

verbose
+++++++

If "-v" or "--verbose" is given, the program shows all calls of external
programs on the console.  The value of this option is stored in the
configuration file.

dry-run
+++++++

If "-n" or "--dry-run" is given, the program just shows what it *would* do.
