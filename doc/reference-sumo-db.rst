sumo-db
=======

What the script does
--------------------

This program manages the dependency database or *DB* file. It is used to create
this file from the output of :doc:`sumo-scan <reference-sumo-scan>` and to
query and change that file.

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

makeconfig {FILE}
+++++++++++++++++

Create a new configuration file from the given options. If the filename is '-'
dump to the console, if it is omitted, rewrite the configuration file that was
read before (see option --config).

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
--config to put these in the configuration file of 
:doc:`"sumo-db "<reference-sumo-db>` or 
:doc:`"sumo-build "<reference-sumo-build>` 

state [STATE] [MODULES]
+++++++++++++++++++++++

Set the :term:`state` for :term:`modules`. This command sets the given STATE
for all the given :term:`modules` and the :term:`dependencies` between the
modules.

weight [WEIGHT] [MODULES]
+++++++++++++++++++++++++

Set the weight factor for modules. Parameter MODULES is a list of
:term:`modulespecs` that specifies the :term:`modules` and :term:`versions` to
operate on. 

Note that this command *does not* use the "--modules" command line option.

Parameter WEIGHT must be an integer.

list
++++

This command lists all :term:`modules` in the 
:ref:`dependency database <reference-sumo-db-The-dependency-database>`.

shownewest {MODULES}
++++++++++++++++++++

This command shows only the newest versions of modules. Mandatory option
"--maxstate" defines the maximum :term:`state` a module may have. 

Optional parameter MODULES specifies which :term:`modules` are shown. If no
:term:`modules` are given the command shows the newest :term:`versions` of all
:term:`modules`.

showall {MODULES}
+++++++++++++++++

This command shows all versions of the given modules. Mandatory option
"--maxstate" defines the maximum :term:`state` a module may have. 

Optional parameter MODULES specifies which :term:`modules` are shown. If no
:term:`modules` are given the command shows all :term:`versions` of all
:term:`modules`.

find [REGEXP]
+++++++++++++

This command shows all :term:`modules` whose names or :term:`sources` match a regexp. 

Mandatory option "--maxstate" defines the maximum :term:`state` a module may
have. Parameter REGEXP is a perl compatible :term:`regular expression`.  

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

cloneversion [MODULE] [OLD-VERSION] [NEW-VERSION] {SOURCESPEC}
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

This command adds a new :term:`version` of a :term:`module` to the
:term:`dependency database` by copying the old :term:`version`. All
:term:`modules` that depend on the old :term:`version` now also depend on the
new :term:`version` of the module. If sourcespec is given, the command changes
the source part according to this parameter. A sourcespec has the form "path
PATH" or "darcs URL" or "darcs URL TAG". Both, URL or TAG may be "*", in this
case the original URL or TAG remains unchanged.

replaceversion [MODULE] [OLD-VERSION] [NEW-VERSION]
+++++++++++++++++++++++++++++++++++++++++++++++++++

This command replaces a :term:`version` of a :term:`module` with a new
:term:`version`. All the data of the :term:`module` is copied. All
:term:`modules` that used to depend on the old :term:`version` now depend on
the new :term:`version`. If sourcespec is given, the command changes the
source part according to this parameter. A sourcespec has the form "path PATH"
or "darcs URL" or "darcs URL TAG". Both, URL or TAG may be "*", in this case
the original URL or TAG remains unchanged.

Options
-------

Here is a short overview on command line options:

--version             show program's version number and exit
-h, --help            show this help message and exit
--summary             Print a summary of the function of the program.
--test                Perform some self tests.
-c FILE, --config FILE  
                      Load options from the given configuration file. You can
                      specify more than one of these, in this case the files
                      are merged. If this option is not given and
                      --no-default-config is not given, the program tries to
                      load the default configuration file sumo-db.config.
--no-default-config   If this option is given the program doesn't load the
                      default configuration.
--db DB               Define the name of the DB file. This option value is
                      stored in the configuration file. 
--dumpdb              Dump the modified db on the console, currently only for the 
                      commands "weight", "merge", "cloneversion" and
                      "replaceversion".
--arch ARCH           Define the name of a targetarchitecture. You can specify
                      more than one target architecture.  You can specify more
                      than one of these by repeating this option or by joining
                      values in a single string separated by spaces.  This
                      option value is stored in the configuration file.  
-m MODULE, --module MODULE  Define a :term:`modulespec`. If you specify modules with
                      this option you don't have to put :term:`modulespecs`
                      after some of the commands. You can specify more than one
                      of these by repeating this option or by joining values in
                      a single string separated by spaces.  This option value
                      is stored in the configuration file.
-b, --brief           Create a more brief output for some commands.
-M STATE, --maxstate STATE      
                      Specify the maximum state for some commands.  This option
                      value is stored in the configuration file.
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
-p, --progress        Show progress on stderr. This option value is stored in
                      the configuration file.
-t, --trace           Switch on some trace messages.
-v, --verbose         Show command calls.  This option value is stored in the
                      configuration file.
-n, --dry-run         Just show what the program would do.
