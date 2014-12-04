sumo
====

What the script does
--------------------

The script has two major purposes:

- Manage the :term:`dependency database` or :term:`DB` file. 
  It is used to create this file from the output of 
  :doc:`sumo-scan <reference-sumo-scan>` and to query and 
  change that file.
- Create and manage :term:`builds`. It also keeps note of 
  all builds in the build database or :term:`BUILDDB`.

The script takes one or mode commands and has a number of options. Single
character options always start with a single dash "-", long options start with
a double dash "--", commands are simple words on the command line.

How it works
------------

Information on all known :term:`modules` and module :term:`versions` is kept in
the :term:`dependency database`. This file also contains a :term:`source`
specification for each module that may be a directory, tar file or a repository
specification.

A complete and consistent set of modules that is compiled is called a
:term:`build`.  All :term:`builds` are kept in a single directory, the
:term:`support directory`. Information on :term:`builds` is kept in a 
`JSON <http://www.json.org>`_ file, the build database or :term:`BUILDDB`.

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
            "dependencies": [
                "BASE"
            ],
            "source": {
                "darcs": {
                    "tag": "R6-2",
                    "url": "rcsadm@aragon.acc.bessy.de:/opt/repositories/controls/darcs/epics/support/bspDep/timer"
                }
            }
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
            "dependencies": [
                "ALARM",
                "BASE",
                "MISC_DBC",
                "MISC_DEBUGMSG",
                "SOFT_DEVHWCLIENT"
            ],
            "source": {
                "darcs": {
                    "tag": "R2-4-0",
                    "url": "rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.12/support/mcan/2-4-0"
                }
            }
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
            "dependencies": [
                "ALARM",
                "BASE",
                "MISC_DBC",
                "MISC_DEBUGMSG",
                "SOFT_DEVHWCLIENT"
            ],
            "source": {
                "darcs": {
                    "tag": "R2-4-1",
                    "url": "rcsadm@aragon.acc.bessy.de:/opt/Epics/R3.14.12/support/mcan/2-4-0"
                }
            }
        },
    },
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
      }
  }

aliasdata
:::::::::

When the support module is to be compiled "sumo build" creates a RELEASE file
from the known dependencies of the module. The RELEASE file contains variable
definitions, one for each dependency whose name is the module name and whose
value is the path of the compiled module. If a module needs a variable name
that is different from the module name, an alias must be defined. For each
dependency that is part of the alias map, the *ALIASNAME* of the alias map is
taken. The *aliasdata* map has this form::

  {
      MODULENAME: MODULEALIAS,
      MODULENAME: MODULEALIAS,
      ...
  }

archdata
::::::::

EPICS support modules may be :term:`architecture` independent or they may
support one or more target architectures. Each target :term:`architecture` in
EPICS has a unique name. The *archdata* map contains a key for each supported
:term:`architecture`. If a module is :term:`architecture` independent, the
*archdata* map contains the special key "ANY". This is the form of the
*archdata* map::

  {
      ARCHNAME: true,
      ARCHNAME: true,
      ...
  }

dependencies
::::::::::::

This is a list of :term:`modules` this :term:`module` depends on. Note that we
do not store the :term:`versions` of the :term:`modules` here. Information on
which :term:`version` is compatible with another :term:`version` can be found
in the build database or :term:`BUILDDB`.  This is the form of the
*dependencies* list::

  [
      MODULENAME,
      MODULENAME,
      ...
  ]

source data
:::::::::::

The *source data* describes where the :term:`sources` of the :term:`module` can
be found. It is a map with a single key. The key either has the value "path",
"tar", "darcs", "hg" or "git". If the key is "path" the  value is a string, the
path of the source. In case of "tar" the value is the name of the tar file. If
the key is "darcs" or "hg", the value is a map. This map has a key "url" whose
value is the repository url. The map may also have a key "tag" which is the
repository tag or a key "rev" which is the revision number.  Here is the
structure of the *source data*::

  {
      "path": PATH
  }

or::

  {
      "tar": TARFILE
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

or::

  {
      "hg": {
          "url": URL
      }
  }

or::

  {
      "hg": {
          "rev": REVISION,
          "url": URL
      }
  }

or::

  {
      "hg": {
          "tag": TAG,
          "url": URL
      }
  }

or::

  {
      "git": {
          "url": URL
      }
  }

or::

  {
      "git": {
          "rev": REVISION,
          "url": URL
      }
  }

or::

  {
      "git": {
          "tag": TAG,
          "url": URL
      }
  }

The scan database
+++++++++++++++++

When :doc:`"sumo-scan all"<reference-sumo-scan>` is used to scan an existing
support directory it also gathers information on what version of a module
depends on what version of another module. In order to keep this information
although the dependency database doesn't contain versions of dependencies, this
information is held in a separate file, the scan database or :term:`SCANDB`.
This file is also created when a :term:`dependency database` is converted from
the old to the new format with command "convert-old".

Here is an example on how this file looks like::

  {
      "AGILENT": {
          "R2-3": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              }
          }
      },
      "AGILENT-SUPPORT": {
          "R0-10": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              }
          },
          "R0-11": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              }
          },
          "R0-12": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              }
          },
          "R0-9-5": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              }
          }
      },
      "ALARM": {
          "R3-7": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              },
              "BSPDEP_TIMER": {
                  "R6-2": "scanned"
              },
              "MISC_DBC": {
                  "R3-0": "scanned"
              }
          },
          "R3-8": {
              "BASE": {
                  "R3-14-12-2-1": "scanned"
              },
              "BSPDEP_TIMER": {
                  "R6-2": "scanned"
              },
              "MISC_DBC": {
                  "R3-0": "scanned"
              }
          }
      }
  }

  The basic datastructure is this::

  {
      MODULENAME: {
          DEPENDENCY_MODULENAME: {
              DEPENDENCY_VERSION: STATE
              DEPENDENCY_VERSION: STATE
              ...
          }
      }
  }

For each dependency of a module this structure contains the version of the
dependency and a state. The state can be "stable" or "testing" or "scanned" but
is always "scanned" if the file was generated with sumo-db.

The build database
++++++++++++++++++

The build database or :term:`BUILDDB` file is a `JSON <http://www.json.org>`_
file that contains information of all :term:`builds` in the 
:term:`support directory`.

Here is an example how this file looks like::

  {
      "001": {
          "modules": {
              "ALARM": "R3-5",
              "ASYN": "R4-15-bessy2",
              "BASE": "R3-14-8-2-0",
              "BSPDEP_CPUBOARDINIT": "R4-0",
              "BSPDEP_TIMER": "R5-1",
              "CSM": "R3-8",
              "EK": "R2-1",
              "GENSUB": "PATH-1-6-1",
              "MCAN": "R2-3-18",
              "MISC": "R2-4",
              "SEQ": "R2-0-12-1",
              "SOFT": "R2-5",
              "VXSTATS": "R2-0"
          },
          "state": "stable"
      },
      "002": {
          "linked": {
              "ASYN": "001",
              "BASE": "001",
              "BSPDEP_CPUBOARDINIT": "001",
              "BSPDEP_TIMER": "001",
              "CSM": "001",
              "EK": "001",
              "GENSUB": "001",
              "MISC": "001",
              "SEQ": "001",
              "SOFT": "001",
              "VXSTATS": "001"
          },
          "modules": {
              "ALARM": "R3-4",
              "ASYN": "R4-15-bessy2",
              "BASE": "R3-14-8-2-0",
              "BSPDEP_CPUBOARDINIT": "R4-0",
              "BSPDEP_TIMER": "R5-1",
              "CSM": "R3-8",
              "EK": "R2-1",
              "GENSUB": "PATH-1-6-1",
              "MCAN": "R2-3-18",
              "MISC": "R2-4",
              "SEQ": "R2-0-12-1",
              "SOFT": "R2-5",
              "VXSTATS": "R2-0"
          },
          "state": "unstable"
      }
  }

The basic datastructure is this::

  {
      BUILDTAG : {
          <builddata> 
          },
      BUILDTAG : {
          <builddata> 
          },
      ...
  }

The *builddata* has this form::

  {
      "linked": {
          <linkdata>
          },
      "modules": {
          <moduledata>
          },
      "state": <state>
  }

moduledata
::::::::::

moduledata is a map that maps :term:`modulenames` to :term:`versionnames`.
This specifies all the :term:`modules` that are part of the :term:`build`.
Since a :term:`build` may reuse :term:`modules` from another :term:`build` not
all modules from this map may actually exist as separate directories of the
:term:`build`. The *moduledata* has this form::

  {
      MODULENAME: VERSIONNAME,
      MODULENAME: VERSIONNAME,
      ...
  }

linkdata
::::::::

linkdata is a map that maps :term:`modulenames` to buildtags. This map contains
all :term:`modules` of the :term:`build` that are reused from other
:term:`builds`. If a :term:`build` has no linkdata, the key "linked" in
*builddata* is omitted. The *linkdata* has this form::

  {
      MODULENAME: BUILDTAG,
      MODULENAME: BUILDTAG,
      ...
  }

state
:::::

This is a :term:`state` string that describes the state of the :term:`build`.
Here are the meanings of the :term:`state` string:

* unstable: the :term:`build` has been created but not yet compiled
* testing: the :term:`build` has been compiled successfully
* stable: the :term:`build` has been tested in production successfully

Configuration Files
+++++++++++++++++++

Many options that can be given on the command line can be taken from
configuration files. For more details see
:doc:`"configuration files "<configuration-files>`.

Commands
--------

You always have to provide sumo with a *maincommand*. Some *maincommands* need
to be followed by a *subcommand*. 

maincommands
++++++++++++

help [command...]
:::::::::::::::::

This command prints help for the given command. It can be invoked as::

  help
  help MAINCOMMAND
  help SUBCOMMAND
  help MAINCOMMAND SUBCOMMAND

You get a list of all known MAINCOMMANDS with::

  help maincommand

makeconfig FILENAME [OPTIONNAMES]
:::::::::::::::::::::::::::::::::

Create a new configuration file from the options read from configuration files
and options from the command line. If FILENAME is '-' dump to the console.
OPTIONNAMES is an optional list of long option names. If OPTIONNAMES are
specified, only options from this list are saved in the configuration file.

edit FILE
:::::::::

Start the editor specified by the environment variable "VISUAL" or "EDITOR"
with that file. This command first aquires a file-lock on the file that is only
released when the editor program is terminated. If you want to edit a
:term:`DB` or :term:`BUILDDB` file directly, you should always do it with this
with this command. The file locking prevents other users to use the file at the
same time you modify it.

This command must be followed by a *filename*.

lock FILE
:::::::::

Lock a FILE, then exit sumo. This is useful if you want to read or write a
database file without sumo interfering. Don't forget to remove the lock later
with the "unlock" command.

This command must be followed by a *filename*.

unlock FILE
:::::::::::

Unlock a FILE, then exit sumo. If you locked a database with "lock" before you
should always unlock it later, otherwise sumo can't access the file.

This command must be followed by a *filename*.

db
::

This is the maincommand for all operations that work with the 
:term:`dependency database` (DB) file.

For all of the db subcommands you have to specify the dependency database with
option --db or a configuration file.

build
:::::

This is the maincommand for all operations that work with builds and the build
database (:term:`BUILDDB`).

For all of the build subcommands you have to specify the dependency database
and the build directory with --db and --builddir or a configuration file.

subcommands for maincommand "db"
++++++++++++++++++++++++++++++++

convert SCANFILE
::::::::::::::::

Convert a :term:`scanfile` that was created by by 
:doc:`"sumo-scan all"<reference-sumo-scan>` to a new dependency database.
If SCANFILE is a dash "-", the program expects the scanfile on stdin.
Note that options "--db" and "--scandb" are
mandatory here. With "--db" you specify the name of the new created 
:ref:`dependency database <reference-sumo-db-The-dependency-database>`
file, with "--scandb" you specify the name of the scan database file. The scan
database file contains information on what moduleversion can be used with what
dependency version.

convert-old OLD-DEPS-DB
:::::::::::::::::::::::

Convert a 
:ref:`dependency database <reference-sumo-db-The-dependency-database>` from the
old to the new format. Note that options "--db" and "--scandb" are mandatory
here. With "--db" you specify the name of the new created 
:ref:`dependency database <reference-sumo-db-The-dependency-database>` file,
with "--scandb" you specify the name of the scan database or :term:`SCANDB`
file. The scan database file contains information on what :term:`version` of a
:term:`module` is probably compatible with what version of a :term:`dependency`
according to the data in the old dependency database.

appconvert SCANFILE
:::::::::::::::::::

Convert a :term:`scanfile` that was created by applying 
:doc:`"sumo-scan all"<reference-sumo-scan>` to an application to a list of 
:term:`aliases` and :term:`modulespecs` in `JSON <http://www.json.org>`_
format. The result is printed to the console. It can be used with
--config to put these in the configuration file of sumo.

weight WEIGHT MODULES
:::::::::::::::::::::

Set the weight factor for modules. A weight determines where a module is placed
in the generated RELEASE file. Modules there are sorted first by weight, then
by dependency. Parameter MODULES is a list of :term:`modulespecs`. Use
modulename:{+-}versionname to select more versions of a module.

Note that this command *does not* use the "--modules" command line option.

Parameter WEIGHT must be an integer.

list
::::

This command lists all :term:`modules` in the 
:ref:`dependency database <reference-sumo-db-The-dependency-database>`.

shownewest [MODULES]
::::::::::::::::::::

This command shows the newest versions of modules by applying some trying to
sort version names intelligently and picking the last in the sort order.

Optional parameter MODULES specifies the names of :term:`modules` shown. If no
:term:`modules` are given the command shows the newest :term:`versions` of all
:term:`modules`.

showall [MODULES]
:::::::::::::::::

This command shows all versions of the given modules. 

Optional parameter MODULES specifies the names of :term:`modules` shown. If no
:term:`modules` are given the command shows all :term:`versions` of all
:term:`modules`.

filter MODULES...
:::::::::::::::::

This command prints only the parts of the dependency database that contain the
given modules. 

Parameter MODULES is a list of :term:`modulespecs` MODULE:{+-}VERSION that
specifies the :term:`modules` and :term:`versions` to operate on. 

find REGEXP
:::::::::::

This command shows all :term:`modules` whose names or :term:`sources` match a
regexp.  Parameter REGEXP is a perl compatible :term:`regular expression`.  

check
:::::

This command does a consistency check of the dependency database (:term:`DB`
file).

merge DB
::::::::

This command merges a :term:`dependency database` with another
:term:`dependency database`. The database that is modified must follow the
command as parameter DB. The database that is added must be specified with the
"--db" option.

cloneversion MODULE OLD-VERSION NEW-VERSION [SOURCESPEC]
::::::::::::::::::::::::::::::::::::::::::::::::::::::::

This command adds a new :term:`version` of a :term:`module` to the
:term:`dependency database` by copying the old :term:`version`. MODULE here is
just the name of the module since the version follows as a separate argument.
If sourcespec is given, the command changes the source part according to this
parameter. A sourcespec has the form "path PATH", "tar TARFILE", "REPOTYPE URL"
or "REPOTYPE URL TAG".  REPOTYPE may be "darcs", "hg" or "git". Both, URL or
TAG may be "*", in this case the original URL or TAG remain unchanged. If
sourcespec is not given, the command adds NEW-VERSION as new tag to the source
specification. The command always asks for a confirmation of the action unless
option "-y" is used.

replaceversion MODULE OLD-VERSION NEW-VERSION
:::::::::::::::::::::::::::::::::::::::::::::

This command replaces a :term:`version` of a :term:`module` with a new
:term:`version`. MODULE here is just the name of the module since the version
follows as a separate argument. All the data of the :term:`module` is copied.
If sourcespec is given, the command changes the source part according to this
parameter. A sourcespec has the form "path PATH", "tar TARFILE", "REPOTYPE URL"
or "REPOTYPE URL TAG".  REPOTYPE may be "darcs", "hg" or "git". Both, URL or
TAG may be "*", in this case the original URL or TAG remains unchanged.

clonemodule OLD-MODULE NEW-MODULE [VERSIONS]
::::::::::::::::::::::::::::::::::::::::::::

Copy all :term:`versions` of the existing old :term:`module` and add this with
the name of thew new :term:`module` to the :term:`dependency` database.
OLD-MODULE and NEW-MODULE here are just the module names since the versions may
follow as a separate argument. If there are no :term:`versions` specified, the
command copies all existing :term:`versions`. Note that this DOES NOT add the
new :term:`module` as :term:`dependency` to any other :term:`modules`.

dependency-delete MODULE DEPENDENCY
:::::::::::::::::::::::::::::::::::

Delete a :term:`dependency` of a :term:`module`. MODULE here is a
:term:`modulespec` of the form MODULE:VERSION that specifies a single version
of a module.

dependency-add MODULE DEPENDENCY
::::::::::::::::::::::::::::::::

Add a :term:`dependency` to a :term:`module`. MODULE here is a
:term:`modulespec` of the form MODULE:VERSION that specifies a single version
of a module.

alias-add MODULE DEPENDENCY ALIAS
:::::::::::::::::::::::::::::::::

Define a new :term:`alias` for a :term:`dependency` of a :term:`module`. MODULE
here is a :term:`modulespec` of the form MODULE:VERSION that specifies a single
version of a module.

subcommands for maincommand "build"
+++++++++++++++++++++++++++++++++++

try MODULES
:::::::::::

This command helps to create :term:`module` specifications for the "new"
command. Each MODULE here is a :term:`modulespec` of the form MODULE or
MODULE:{+-}VERSION that specifies just a module name, a module and some
versions or a single version. You can specify an incomplete list of
:term:`modules`.  The program then shows which :term:`modules` you have to
include in your list since other :term:`modules` depend on them and shows
information on all :term:`versions` of all :term:`modules` that satisfy your
:term:`module` specifications. It also shows if your :term:`module`
specifications are *complete* and *exact* meaning that all :term:`dependencies`
are included and all :term:`modules` are specified with exactly a single
:term:`version`.  Note that you can use option "--scandb" in order to give
additional information which :term:`versions` of :term:`modules` are compatible
with each other. 

With option "--brief" or "-b", the output of the command is a shorter summary
which is in many cases all you want to see.

For an example see :ref:`try example <example-sumo-build-try>`.

new MODULES
:::::::::::

This command creates a new :term:`build`. Each module given in MODULES here is
a :term:`modulespec` of the form MODULE:VERSION that specifies a single version
of a module. If the :term:`buildtag` is not given as an option, the program
generates a :term:`buildtag` in the form "AUTO-nnn". A new :term:`build` is
created according to the :term:`modulespecs`. Your modulespecifications must be
*complete* and *exact* meaning that all :term:`dependencies` are included and
all :term:`modules` are specified with exactly a single :term:`version`. Use
command "try" in order to create :term:`module` specifications that can be used
with command "new".  This command calls "make" and, after successful
completion, sets the state of the :term:`build` to "testing". If you want to
skip this step, use option "--no-make". In order to provide arbitrary options
to make use option "--makeopts". 

find MODULES
::::::::::::

This command is used to find matching :term:`builds` for a given list of
:term:`modulespecs`. Each module in MODULES here is a :term:`modulespec` of the
form MODULE or MODULE:{+-}VERSION that specifies just a module name, a module
and some versions or a single version. The command prints a list of
:term:`buildtags` of matching :term:`builds` on the console. If option --brief
is given, the program just shows the buildtags. 

useall BUILDTAG
:::::::::::::::

This command creates a configure/RELEASE file for an application. The command
must be followed by buildtag. The release file created includes *all*
:term:`modules` of the :term:`build`. The buildtag may be given as argument or
option. Output to another file or the console can be specified with option
'-o'. 

use MODULES
:::::::::::

This command creates a configure/RELEASE file for an application. Each module
given in MODULES here is a :term:`modulespec` of the form MODULE:VERSION that
specifies a single version of a module. If option --buildtag is given, it
checks if this is compatible with the given :term:`modules`.  Otherwise it
looks for all :term:`builds` that have the :term:`modules` in the required
:term:`versions`. If more than one matching :term:`build` found it takes the
one with the alphabetically first buildtag. The RELEASE file created includes
only the :term:`modules` that are specified. Output to another file or the
console can be specified with option '-o'.

list
::::

This command lists the names of all builds.

show BUILDTAG
:::::::::::::

This command shows the data of a :term:`build`. The :term:`buildtag` must be
given as an argument.

state BUILDTAG [NEW-STATE]
::::::::::::::::::::::::::

This command is used to show or change the :term:`state` of a :term:`build`.
The :term:`buildtag` must be given as an argument. If there is no new
:term:`state` given, it just shows the current :term:`state` of the
:term:`build`. Otherwise the :term:`state` of the :term:`build` is changed
to the given value. 

delete BUILDTAG
:::::::::::::::

If no other :term:`build` depends on the :term:`build` specified by the
:term:`buildtag`, the directories of the :term:`build` are removed and it's
entry in the builddb is deleted. The :term:`buildtag` must be given as an
argument.

cleanup BUILDTAG
::::::::::::::::

This command removes the remains of a failed :term:`build`. If the command
"new" is interrupted or stopped by an exception in the program, the
:term:`build` may be in an incomplete :term:`state`. In this case you can use
the "cleanup" command to remove the directories of the failed :term:`build`.
The :term:`buildtag` must be given as an argument.

Options
-------

.. _reference-sumo-Options:

Here is a short overview on command line options:

``--version``
    show program's version number and exit
``-h, --help``
    show this help message and exit
``--summary``
    Print a summary of the function of the program.
``--test``
    Perform some self tests.
``-c FILE, --config FILE``
    Load options from the given configuration file. You can specify more than
    one of these.  Unless --no-default-config is given, the program always
    loads configuration files from several standard directories first before it
    loads your configuration file. The contents of all configuration files are
    merged.
``-C, --no-default-config``
    If this option is not given and --no-default-config is not given, the
    program tries to load the default configuration file sumo-scan.config from
    several standard locations (see documentation on configuration files).
``--mergeoption OPTIONNAME``
    If an option with name OPTIONNAME is given here and it is a list option,
    the lists from the configuration file and the command line are merged. The
    new list is the sum of both lists where it is ensured that for all elements
    the string up to the first colon ':' is unique (this is useful for module
    specifications that have the form 'module:version').
``--#preload FILES`` 
    Specify a an '#preload' directive in the configuration file. This option
    has only a meaning if a configuration file is created with the 'makeconfig'
    command. '#preload' means that the following file(s) are loaded before the
    rest of the configuration file.
``--#opt-preload FILES`` 
    This option does the same as --#preload but the file loading is optional.
    If they do not exist the program continues without an error.
``--#postload FILES`` 
    Specify a an '#postload' directive in the configuration file. This option
    has only a meaning if a configuration file is created with the 'makeconfig'
    command. '#postload' means that the following file(s) are loaded after the
    rest of the configuration file.
``--#opt-postload FILES`` 
    This option does the same as --#postload but the file loading is optional.
    If they do not exist the program continues without an error.
``--db DB``
    Define the name of the DB file. A default for this option can be put in a
    configuration file.
``--dbrepomode MODE``
    Specify how sumo should use the dependency database repository. There are
    three possible values: 'get', 'pull' and 'push'. With 'get' the foreign
    repository is cloned if the local repository does not yet exist. With
    'pull' sumo does a pull and merge before each read operation on the
    database. With 'push' it additionally does a push after each modification
    of the database. The default is 'get'." A default for this option can be
    put in a configuration file.
``--dbrepo REPOSITORY``
    Define a REPOSITORY for the db file. REPOSITORY must consist of 'REPOTYPE
    URL', REPOTYPE may be 'darcs', 'hg' or 'git'. Option --db must specify a
    file path whose directory part will contain the repository for the db file.
    Before reading the db file a 'pull' command will be executed. When the file
    is changed, a 'commit' and a 'push' command will be executed. If the
    repository doesn't exist the program tries to check out a working copy from
    the given URL. A default for this option can be put in a configuration
    file.
``--scandb SCANDB``
    Specify the (optional) :term:`SCANDB` file. The scan database file contains
    information on what moduleversion can be used with what dependency version.
``--dumpdb``
    Dump the modified db on the console, currently only for the commands
    "weight", "merge", "cloneversion" and "replaceversion".
``--logmsg`` LOGMESSAGE
    Specify a logmessage for automatic commits when --dbrepo is used.
``-t BUILDTAG, --buildtag BUILDTAG``
    Specify a buildtag.
``--buildtag-stem STEM``
    Specify the stem of a buildtag. This option has only an effect on the
    commands 'new' and 'try' if a buildtag is not specified. The program
    generates a new tag in the form 'stem-nnn' where 'nnn' is the smallest
    possible number that ensures that the buildtag is unique.
``--builddir BUILDDIR``
    Specify the support directory. If this option is not given take the current
    working directory as support directory. A default for this option can be
    put in a configuration file.
``-o OUTPUTFILE, --output OUTPUTFILE``
    Define the output for commands 'useall' and 'use'. If this option is not
    given, 'useall' and 'use' write to 'configure/RELEASE'. If this option is
    '-', the commands write to standard-out",
``-x EXTRALINE, --extra EXTRALLINE``
    Specify an extra line that is added to the generated RELEASE file. A
    default for this option can be put in a configuration file.
``-a ALIAS, --alias ALIAS``
    Define an alias for the commands 'use' and 'useall'. An alias must have the
    form FROM:TO. The path of module named 'FROM' is put in the generated
    RELEASE file as a variable named 'TO'. You can specify more than one of
    these by repeating this option or by joining values in a single string
    separated by spaces. A default for this option can be put in a
    configuration file.
``--arch ARCH``
    Define the name of a targetarchitecture. You can specify more than one
    target architecture.  You can specify more than one of these by repeating
    this option or by joining values in a single string separated by spaces. A
    default for this option can be put in a configuration file.
``-m MODULE, --module MODULE``
    Define a :term:`modulespec`. If you specify modules with this option you
    don't have to put :term:`modulespecs` after some of the commands. You can
    specify more than one of these by repeating this option or by joining
    values in a single string separated by spaces. A default for this option
    can be put in a configuration file.
``-X, --exclude-states``
    For command 'try' exclude all 'dependents' whose state does match one of
    the regular expressions (REGEXP).
``-b, --brief``
    Create a more brief output for some commands.
``-D EXPRESSION, --dir-patch EXPRESSION``
    Specify a directory patchexpression. Such an expression consists of a tuple
    of 2 python strings. The first is the match expression, the second one is
    the replacement string. The regular expression is applied to every source
    path generated. You can specify more than one patchexpression. A default
    for this option can be put in a configuration file.
``-U EXPRESSION, --url-patch EXPRESSION``
    Specify a repository url patchexpression. Such an expression consists of a
    tuple of 2 python strings. The first is the match expression, the second
    one is the replacement string. The regular expression is applied to every
    source url generated. You can specify more than one patchexpression. A
    default for this option can be put in a configuration file.
``--noignorecase``
    For command 'find', do NOT ignore case.
``--no-checkout``
    With this option, "new" does not check out sources of support modules. This
    option is only here for test purposes.
``--no-make``
    With this option, "new" does not call "make".j
``--makeopts MAKEOPTIONS``
    Specify extra option strings for make You can specify more than one of
    these by repeating this option or by joining values in a single string
    separated by spaces. A default for this option can be put in a
    configuration file.
``--readonly``
    Do not allow modifying the database files or the support directory. A
    default for this option can be put in a configuration file.
``--nolock``
    Do not use file locking.
``-p, --progress``
    Show progress on stderr. A default for this option can be put in a
    configuration file.
``--trace``
    Switch on some trace messages.
``--tracemore``
    Switch on even more trace messages.
``--dump-modules``
    Dump module specs, then stop the program.
``--list``
    Show information for automatic command completion.
``-y, --yes``
    All questions the program may ask are treated as if the user replied 'yes'.
``--exceptions``
    On fatal errors that raise python exceptions, don't catch these. This will
    show a python stacktrace instead of an error message and may be useful for
    debugging the program."
``-v, --verbose``
    Show command calls. A default for this option can be put in a
    configuration file.
``-n, --dry-run``
    Just show what the program would do.
