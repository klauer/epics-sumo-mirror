sumo-db
=======

What the script does
--------------------

This program manages the dependency database or *DB* file. It is used to create
this file from the output of :doc:`sumo-scan <reference-sumo-scan>`, to change
this file and to create a *partialdb* file that is used by the
:doc:`sumo-build <reference-sumo-build>` script.

The script takes one or mode commands and has a number of options. Single
character options always start with a single dash "-", long options start with
a double dash "--", commands are simple words on the command line.

How it works
------------


.. _reference-sumo-db-The-dependency-database:

The dependency database
+++++++++++++++++++++++

The dependency database or :term:`DB` file is a `JSON <http://www.json.org>`_ file
that contains information on versions of support modules and their
dependencies. Here is an example how this file looks like::

  {
      "BSPDEP_TIMER": {
          "R6-2": {
              "aliases": {
                  "BASE": "EPICS_BASE"
              },
              "archs": {
                  "RTEMS-mvme2100": true,
                  "RTEMS-mvme5500": true,
                  "vxWorks-68040": true,
                  "vxWorks-ppc603": true
              },
              "dependencies": {
                  "BASE": {
                      "R3-14-12-2-1": "stable"
                  }
              },
              "source": {
                  "darcs": {
                      "tag": "R6-2",
                      "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/support/bspDep/timer"
                  }
              },
              "state": "stable"
          }
      },
      "MCAN": {
          "R2-4-0": {
              "aliases": {
                  "BASE": "EPICS_BASE",
                  "MISC_DBC": "DBC",
                  "MISC_DEBUGMSG": "DEBUGMSG",
                  "SOFT_DEVHWCLIENT": "DEVHWCLIENT"
              },
              "archs": {
                  "vxWorks-68040": true,
                  "vxWorks-ppc603": true
              },
              "dependencies": {
                  "ALARM": {
                      "R3-7": "stable"
                  },
                  "BASE": {
                      "R3-14-12-2-1": "stable"
                  },
                  "MISC_DBC": {
                      "R3-0": "stable"
                  },
                  "MISC_DEBUGMSG": {
                      "R3-0": "stable"
                  },
                  "SOFT_DEVHWCLIENT": {
                      "R3-0": "stable"
                  }
              },
              "source": {
                  "darcs": {
                      "tag": "R2-4-0",
                      "url": "rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.12/support/mcan/2-4-0"
                  }
              },
              "state": "stable"
          },
          "R2-4-1": {
              "aliases": {
                  "BASE": "EPICS_BASE",
                  "MISC_DBC": "DBC",
                  "MISC_DEBUGMSG": "DEBUGMSG",
                  "SOFT_DEVHWCLIENT": "DEVHWCLIENT"
              },
              "archs": {
                  "vxWorks-68040": true,
                  "vxWorks-ppc603": true
              },
              "dependencies": {
                  "ALARM": {
                      "R3-7": "stable"
                  },
                  "BASE": {
                      "R3-14-12-2-1": "stable"
                  },
                  "MISC_DBC": {
                      "R3-0": "stable"
                  },
                  "MISC_DEBUGMSG": {
                      "R3-0": "stable"
                  },
                  "SOFT_DEVHWCLIENT": {
                      "R3-0": "stable"
                  }
              },
              "source": {
                  "darcs": {
                      "tag": "R2-4-1",
                      "url": "rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.12/support/mcan/2-4-0"
                  }
              },
              "state": "stable"
          }
      }
  }

The basic datastructure is this::

  {
      MODULENAME : {
          VERSIONNAME : {
              <versiondata>
          },
          VERSIONNAME : {
              <versiondata>
          },
          ...
      }
  }

The *versiondata* map has this form::

  {
      "aliases": {
          <aliasdata>
      },
      "archs": {
          <archdata>
      },
      "dependencies": {
          <dependency data>
      },
      "source": {
          <source data>
      },
      "state": STATE
  }

aliasdata
:::::::::

When the support module is to be compiled, 
:doc:`sumo-build <reference-sumo-build>` creates a RELEASE file from the known
dependencies of the module. The RELEASE file contains variable definitions, one
for each dependency whose name is the module name and whose value is the path
of the compiled module. If a module needs a variable name that is different
from the module name, an alias must be defined. For each dependency that is
part of the alias map, the *ALIASNAME* of the alias map is taken. The
*aliasdata* map has this form::

  {
      MODULENAME: MODULEALIAS,
      MODULENAME: MODULEALIAS,
      ...
  }

archdata
::::::::

EPICS support modules may be architecture independent or they may support one
or more target architectures. Each target architecture in EPICS has a unique
name. The *archdata* map contains a key for each supported architecture. If a
module is architecture independent, the *archdata* map contains the special key
"ANY". This is the form of the *archdata* map::

  {
      ARCHNAME: true,
      ARCHNAME: true,
      ...
  }

dependencies
::::::::::::

This is a map that has a key for each module this module depends on. The value
for each key is a map where keys are names of supported versions and values are
*STATES*. A *STATE* is one of the strings "stable", "testing" or "unstable".
This indicates how well the dependency is tested. This is the form of the
*dependencies* map::

  {
      MODULENAME: {
          VERSIONNAME: STATE,
          VERSIONNAME: STATE,
          ...
      },
      MODULENAME: {
          VERSIONNAME: STATE,
          VERSIONNAME: STATE,
          ...
      },
      ...
  }

source data
:::::::::::

The *source data* describes where the sources of the module can be found. It is a map with a single key. The key either has the value "path" or "darcs". If the key is "path" the  value is a string, the path of the source. If the key is "darcs", the value is a map. This map has a key "url" whose value is the repository url. The map may also have a key "tag" which is the repository tag. Here is the structure of the *source data*::

  {
      "path": PATH
  }

or::

  {
      "darcs": {
          "url": URL
      }
  }

or::

  {
      "darcs": {
          "tag": TAG,
          "url": URL
      }
  }

state
:::::

This defines the *STATE* of the moduleversion. A *STATE* is one of the strings "stable", "testing" or "unstable". It describes how well the moduleversion is tested.

Commands
--------

This is a list of all commands:

edit [FILE]
+++++++++++

Start the editor specified by the environment variable "VISUAL" or "EDITOR"
with that file. This command first aquires a file-lock on the file that is only
released when the editor program is terminated. If you want to edit a
:term:`DB` or :term:`BUILDDB` file directly, you should always do it with this
with this command. The file locking prevents other users to use the file at the
same time you modify it.

This command must be followed by a *filename*.

convert [STATE] [SCANFILE]
++++++++++++++++++++++++++

Convert a :term:`scanfile` that was created by by 
:doc:`"sumo-scan all"<reference-sumo-scan>` to a new depedency database or
:term:`DB` file. All :term:`dependencies` are marked with the specified
:term:`state`.

If SCANFILE is a dash "-", the program expects the scanfile on stdin.

The dependency database file is always printed to the console.

appconvert [SCANFILE]
+++++++++++++++++++++

Convert a :term:`scanfile` that was created by applying 
:doc:`"sumo-scan all"<reference-sumo-scan>` to an application to a list of 
:term:`aliases` and :term:`modulespecs` in `JSON <http://www.json.org>`_
format. The result is printed to the console. It can be used with
--update-config to put these in the configuration file of 
:doc:`"sumo-db "<reference-sumo-db>` or 
:doc:`"sumo-build "<reference-sumo-build>` 

distribution [MAXSTATE] [MODULES]
+++++++++++++++++++++++++++++++++

This command creates a :term:`distribution` from a dependency database or
:term:`DB` file. Parameter MAXSTATE is the maximum :term:`state` of
:term:`dependencies` that are taken into account. Parameter MODULES is a list
of :term:`modulespecs` with *unspecified* or *exactly specified*
:term:`versions`.

For modules with *unspecified* version, the algorithm that selects
:term:`versions` of :term:`modules` tries to find the newest version that is
consistent with the modules with *exactly specified* :term:`versions`. 

The algorithm selects :term:`versions` of modules in the order :term:`modules`
are given to the command. If you have at least two :term:`modules` with an
*unspecified* version, changing the order of :term:`modulespecs` given to the
command may lead to different results.

The output of this command is a 
`JSON <http://www.json.org>`_ structure that has the same format as the
:ref:`dependency database <reference-sumo-db-The-dependency-database>`.

It is, in fact, a part of the dependency database where only one version is
listed for each :term:`module` that is to be included in the
:term:`distribution`. This is also called a :term:`partialdb` since it is a
partial database.

The :term:`partialdb` file is used by the script :doc:`sumo-build
<reference-sumo-build>` to create a :term:`build`.

weight [WEIGHT] [MODULES]
+++++++++++++++++++++++++

Set the weight factor for modules. Parameter MODULES is a list of
:term:`modulespecs` that specifies the :term:`modules` and :term:`versions` to
operate on. 

Note that this command *does not* use the "--modules" command line option.

Parameter WEIGHT must be an integer.

show
++++

This command shows all :term:`modules` in the 
:ref:`dependency database <reference-sumo-db-The-dependency-database>`.

shownewest [MAXSTATE] {MODULES}
+++++++++++++++++++++++++++++++

This command shows only the newest versions of modules. It must be followed by
the parameter *maximum state* and it may be followed by a whitespace separated
list of :term:`modulenames`. 

Parameter MAXSTATE is the maximum :term:`state` a module may have. Optional
parameter MODULES specifies which :term:`modules` are shown. If no
:term:`modules` are given the command shows the newest :term:`versions` of all
:term:`modules`.

showall [MAXSTATE] {MODULES}
++++++++++++++++++++++++++++

This command shows all versions of the given modules. It must be followed by
the parameter *maximum state* and it may be followed by a whitespace separated
list of :term:`modulenames`. 

Parameter MAXSTATE is the maximum :term:`state` a module may have. Optional
parameter MODULES specifies which :term:`modules` are shown. If no
:term:`modules` are given the command shows all :term:`versions` of all
:term:`modules`.

find [MAXSTATE] [REGEXP]
++++++++++++++++++++++++

This command shows all :term:`modules` whose names or :term:`sources` match a regexp. 

Parameter MAXSTATE is the maximum :term:`state` a module may have. Parameter
REGEXP is a perl compatible :term:`regular expression`.  

check
+++++

This command does a consistency check of the dependency database (:term:`DB`
file).

merge [DB]
++++++++++

This command merges a :term:`dependency database` with another
:term:`dependency database`. The database that is modified must follow the
command as parameter DB. The database that is added must be specified with the
"--db" option.

filter [MODULES]
++++++++++++++++

This command prints only the parts of the dependency database that contain the
given modules. 

Parameter MODULES is a list of :term:`modulespecs` that specifies the
:term:`modules` and :term:`versions` to operate on. 

If called with option "--savedb", the db file is overwritten with the result.

cloneversion [MODULE] [OLD-VERSION] [NEW-VERSION]
+++++++++++++++++++++++++++++++++++++++++++++++++

This command adds a new :term:`version` of a :term:`module` to the
:term:`dependency database` by copying the old :term:`version`. All
:term:`modules` that depend on the old :term:`version` now also depend on the
new :term:`version` of the module. If you do this you must update the module
:term:`source` definition of the new :term:`version` by editing the
:term:`dependency database` file directly.

replaceversion [MODULE] [OLD-VERSION] [NEW-VERSION]
+++++++++++++++++++++++++++++++++++++++++++++++++++

This command replaces a :term:`version` of a :term:`module` with a new
:term:`version`. All the data of the :term:`module` is copied. All
:term:`modules` that used to depend on the old :term:`version` now depend on
the new :term:`version`.

Options
-------

Here is a short overview on command line options:

--version             show program's version number and exit
-h, --help            show this help message and exit
--summary             Print a summary of the function of the program.
--doc                 Print a longer description of the program (deprecated).
--test                Perform some self tests.
-c FILE, --config FILE
                      Specify the name of the configuration file. If this
                      option is not given try to read from "sumo-db.config" in
                      the current working directory.
--make-config FILE    Create a new config file FILE from the given options. If
                      the filename is '-' dump to the console, if it is an
                      empty string, rewrite the config file that was read
                      before (see option --config).
--update-config FILE  Update options taken from the configuration file with
                      options taken from another file which must be a JSON
                      file. Options from FILE overwrite options taken from the
                      configuration file. Options in FILE that are unknown to
                      the program are ignored.
--db DB               Define the name of the DB file. This option value is
                      stored in the configuration file. 
--savedb              Resave db if it was modified. This option has only a
                      meaning for the commands "merge","filter", "cloneversion"
                      and "replaceversion".
--arch ARCH           Define the name of a targetarchitecture. You can specify
                      more than one target architecture.  You can specify more
                      than one of these by repeating this option or by joining
                      values in a single string separated by spaces.  This
                      option value is stored in the configuration file.
-m MODULE, --module MODULE
                      Define a :term:`modulespec`. If you specify modules with
                      this option you don't have to put :term:`modulespecs`
                      after commands like 'find' or 'use'.  You can specify
                      more than one of these by repeating this option or by
                      joining values in a single string separated by spaces.
                      This option value is stored in the configuration file.
-b, --brief           Create a more brief output for some commands.
-P EXPRESSION, --source-patch EXPRESSION
                      Specify a source patchexpression. Such an expression
                      consists of a tuple of 2 python strings. The first is the
                      match expression, the second one is the replacement
                      string. The regular expression is applied to every source
                      url generated. You can specify more than one
                      patchexpression.  This option value is stored in the
                      configuration file.
--noignorecase        For command 'find', do NOT ignore case.
--nolock              Do not use file locking.
-p, --progress        Show progress on stderr.  This option value is stored in
                      the configuration file.
-t, --trace           Switch on some trace messages.
-v, --verbose         Show command calls.  This option value is stored in the
                      configuration file.
-n, --dry-run         Just show what the program would do.
