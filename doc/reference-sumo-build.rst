sumo-build
==========

What the script does
--------------------

This script creates and manages builds.

The script takes one or mode commands and has a number of options. Single
character options always start with a single dash "-", long options start with
a double dash "--", commands are simple words on the command line.

How it works
------------

All :term:`builds` are kept in a single directory, the 
:term:`support directory`. Information on :term:`builds` is kept in a 
`JSON <http://www.json.org>`_ file, the build database or :term:`BUILDDB`.

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

try [MODULES]
+++++++++++++

This command helps to create :term:`module` specifications for the "new"
command.  You can specify an incomplete list of :term:`modules`,
:term:`modules` without :term:`versions` or with :term:`version` ranges.  The
program then shows which :term:`modules` you have to include in your list since
other :term:`modules` depend on them and shows information on all
:term:`versions` of all :term:`modules` that satisfy your :term:`module`
specifications. It also shows if your :term:`module` specifications are
*complete* and *exact* meaning that all :term:`dependencies` are included and
all :term:`modules` are specified with exactly a single :term:`version`.  Note
that you can use option "--scandb" in order to give additional information
which :term:`versions` of :term:`modules` are compatible with each other.
Options "--db" and "--builddb" are mandatory for this command.

For an example see :ref:`try example <reference-sumo-build-try-example>`.

new [MODULES]
+++++++++++++

This command creates a new :term:`build`. If the :term:`buildtag` is not given
as an option, the program generates a :term:`buildtag` in the form "AUTO-nnn".
Note that options "--db" and "--builddb" are mandatory for this command. A new
:term:`build` is created according to the :term:`modulespecs`. Your
modulespecifications must be *complete* and *exact* meaning that all
:term:`dependencies` are included and all :term:`modules` are specified with
exactly a single :term:`version`. Use command "try" in order to create
:term:`module` specifications that can be used with command "new".  This
command calls "make" and, after successful completion, sets the state of the
:term:`build` to "testing". If you want to skip this step, use option
"--no-make". In order to provide arbitrary options to make use option
"--makeopts".

find [MODULESPECS]
++++++++++++++++++

This command is used to find matching :term:`builds` for a given list of
:term:`modulespecs`. It prints a list of :term:`buildtags` of matching
:term:`builds` on the console. Note that the :term:`versions` in
:term:`modulespecs` may be *unspecified*, *specified exactly* or 
*specifed by relation*.

useall [BUILDTAG]
+++++++++++++++++

This command creates a configure/RELEASE file for an application. The command
must be followed by buildtag. The release file created includes *all*
:term:`modules` of the :term:`build`. The buildtag may be given as argument or
option. Output to another file or the console can be specified with option
'-o'.

use [MODULES]
+++++++++++++

This command creates a configure/RELEASE file for an application. The command
must be followed by a list of :term:`modulespecs`. If option --buildtag is
given, it checks if this is compatible with the given :term:`modules`.
Otherwise it looks for all :term:`builds` that have the :term:`modules` in the
required :term:`versions`. If more than one matching :term:`build` found it
takes the one with the alphabetically first buildtag. Note that the
:term:`modulespecs` MUST specify :term:`versions` exactly. If you have
unspecified :term:`versions` or :term:`versions` specified by relation you must
use command "use" instead.  The RELEASE created includes only the
:term:`modules` that are specified. For this command the :term:`DB` file must
be specified with the "--db" option. Output to another file or the console can
be specified with option '-o'.

list
++++

This command lists the names of all builds.

show [BUILDTAG]
+++++++++++++++

This command shows the data of a :term:`build`. The :term:`buildtag` may be
given as argument or option.

state [BUILDTAG] {NEW STATE}
++++++++++++++++++++++++++++

This command is used to show or change the :term:`state` of a :term:`build`.
The :term:`buildtag` may be given as argument or option.If there is no new
:term:`state` given, it just shows the current :term:`state` of the
:term:`build`. Otherwise the :term:`state` of the :term:`build` is changed to
the given value. 

delete [BUILDTAG]
+++++++++++++++++

If no other :term:`build` depends on the :term:`build` specified by the
:term:`buildtag`, the directories of the :term:`build` are removed and it's
entry in the builddb is deleted. The :term:`buildtag` may be given as argument
or option.

cleanup [BUILDTAG]
++++++++++++++++++

This command removes the remains of a failed :term:`build`. If the command
"new" is interrupted or stopped by an exception in the program, the
:term:`build` may be in an incomplete :term:`state`. In this case you can use
the "cleanup" command to remove the directories of the failed :term:`build`.
The :term:`buildtag` may be given as argument or option.

Options
-------

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
    one of these, in this case the files are merged. If this option is not
    given and --no-default-config is not given, the program tries to load the
    default configuration file sumo-build.config.
``--no-default-config``
    If this option is given the program doesn't load the default configuration.
``--#include FILE`` 
    Specify a an '#include' directive in the configuration file.  This option
    has only a meaning if a configuration file is created with the 'makeconfig'
    command. '#include' means that the following file(s) are included before
    the rest of the configuration file.
``--db DB``
    Define the name of the DB file. This option value is stored in the
    configuration file. 
``--builddb BUILDDB``
    Specify the :term:`BUILDDB` file. This option value is stored in the
    configuration file.
``--scandb SCANDB``
    Specify the (optional) :term:`SCANDB` file. The scan database file contains
    information on what moduleversion can be used with what dependency version.
``-t BUILDTAG, --buildtag BUILDTAG``
    Specify a buildtag.
``--buildtag-stem STEM``
    Specify the stem of a buildtag. This option has only an effect on the
    commands 'new' and 'try' if a buildtag is not specified. The program
    generates a new tag in the form 'stem-nnn' where 'nnn' is the smallest
    possible number that ensures that the buildtag is unique.
``--supportdir SUPPORDIR``
    Specify the support directory. If this option is not given take the current
    working directory as support directory.  This option value is stored in the
    configuration file.
``-x EXTRALINE, --extra EXTRALLINE``
    Specify an extra line that is added to the generated RELEASE file. This
    option value is stored in the configuration file.
``-a ALIAS, --alias ALIAS``
    Define an alias for the commands 'use' and 'useall'. An alias must have the
    form FROM:TO. The path of module named 'FROM' is put in the generated
    RELEASE file as a variable named 'TO'. You can specify more than one of
    these by repeating this option or by joining values in a single string
    separated by spaces. This option value is stored in the configuration file.
``--arch ARCH``
    Define the name of a targetarchitecture. You can specify more than one
    target architecture.  You can specify more than one of these by repeating
    this option or by joining values in a single string separated by spaces.
    This option value is stored in the configuration file.
``-m MODULE, --module MODULE``
    Define a :term:`modulespec`. If you specify modules with this option you
    don't have to put :term:`modulespecs` after some of the commands. You can
    specify more than one of these by repeating this option or by joining
    values in a single string separated by spaces.  This option value is stored
    in the configuration file.
``--modules-from-build BUILDTAG``
    Take the module specifications from a build. If you use "--addmodules" you
    can modify single module specifications in order to create a new build.
``-X, --exclude-states``
    For command 'try' exclude all 'dependents' whose state does match one of
    the regular expressions (REGEXP).
``-b, --brief``
    Create a more brief output for some commands.
``--no-checkout``
    With this option, "new" does not check out sources of support modules. This
    option is only here for test purposes.
``--no-make``
    With this option, "new" does not call "make".j
``--makeopts MAKEOPTIONS``
    Specify extra option strings for make You can specify more than one of
    these by repeating this option or by joining values in a single string
    separated by spaces.  This option value is stored in the configuration
    file.
``--readonly``
    Do not allow modifying the database files or the support directory.  This
    option value is stored in the configuration file.
``--nolock``
    Do not use file locking.
``-p, --progress``
    Show progress on stderr. This option value is stored in the configuration
    file.
``--trace``
    Switch on some trace messages.
``--tracemore``
    Switch on even more trace messages.
``--dump-modules``
    Dump module specs, then stop the program.
``-v, --verbose``
    Show command calls.  This option value is stored in the configuration file.
``-n, --dry-run``
    Just show what the program would do.

Examples
--------

command "try"
+++++++++++++

.. _reference-sumo-build-try-example:

Since the report of the "try" command is a bit complex, here is an example.

The output of "try" is in most cases very long, so you probably want to redirect it to a file transfer it to a pager program like "less". In the following examples we use "less". Note that in "less" you go back with "b", forward with <space> and quit the program with "q". There are many other commands, use "man less" to learn more. "less" is not available on windows platforms.

We assume that you have a configuration file "sumo-build.config" which contains
the settings for all needed command line options and a list of modules. Then we
start the program in our application directory like this::

  sumo-build try | less

In this example we see at the start of the output::

  Not all dependencies were included in module specifications, these modules
  have to be added:
      ALARM
      MISC_DBC

This means that the two mentioned modules are needed by other modules so we
have to add them to our module specifications. We add them on the command line
for now::
  
  sumo-build try ALARM MISC_DBC | less

At the start of the output we now see::

  Not all modules have exactly specified versions. These modules need an 
  exact version specification:
      ALARM
      MISC_DBC             -> suggested version: R3-0

The two modules need a version specification. For "MISC_DBC" the program has
found that you can only use one version, "R3-0" so we can use this. For "ALARM"
we have no further hints, so we have to investigate the rest of the report.
Further below you find::

  List of modules that fullfill the given module specification:

When we look for "ALARM" further below we find::

    "ALARM": {
        "R3-7": {
            "built": false,
            "dependents": {
                "MCAN:TAGLESS-2-6-3": "state: not tested"
            }
        },
        "R3-8": {
            "built": true,
            "dependents": {
                "MCAN:TAGLESS-2-6-3": "state: stable"
            }
        }
    },
  
We see that there are two versions of "ALARM", "R3-7" and "R3-8". Property "built" shows us, if the this version has been built with sumo, so we know that it can be compiled. "dependents" shows which other modules of our module specification list depend on "ALARM". In this case it is only "MCAN:TAGLESS-2-6-3". The "state" property shows what we know about this relation. These are possible values of the state:

state: no tested
  This means that there is no information if these modules are compatible,
  that they can be used together in a build or that they work.

state: scanned
  This means that these modules were used together in a support directory but
  only without sumo. 

state: testing
  This means that these modules have been used in a build and that the state of
  that build was marked "stable".

state: stable
  This means that these modules have been used in a build and that the state of
  that build was marked "stable".

If we look even further below for "ALARM" we find::

    "BASE": {
        "R3-14-12-2-1": {
            "built": true,
            "dependents": {
                "AGILENT-SUPPORT:R0-11": "state: stable",
                "AGILENT:R2-3": "state: stable",
                "ALARM:R3-7": "state: not tested",
                "ALARM:R3-8": "state: stable",
                "APPS_GENERICBOOT:R0-8-3": "state: stable",
                "APPS_GENERICTEMPLATE:R3-7": "state: stable",
                "APPS_IOCWATCH:R3-1": "state: stable",
                ...
            }
        }
    }

This means that "ALARM:R3-7" and "ALARM:R3-8" depend on "BASE:R3-14-12-2-1". We
see only this version of "BASE" here since we have specified exactly this
version of base in our module specifications. We see that "ALARM:R3-8" was in a
build with "BASE:R3-14-12-2-1" and that this build was marked "stable".

So we decide the use "ALARM:R3-8" and "MISC_DBC:R3-0". We use command "try"
again::

  sumo-build try ALARM:R3-8 MISC_DBC:R3-0 | less

Now we see at the start of the output::

  The following modules are not needed by other modules in your module
  specification:
      AGILENT
      AGILENT-SUPPORT
      ...

This is an overview of modules that are not needed by other modules in your
module specifications. You may use this to remove modules that your application
doesn't need, in this case you would remove them in your configuration file.

We see at the end of the output::

  Command 'new' would create build with tag 'AUTO-001'
  
  Your module specifications are complete. You can use these with command
  'new' to create a new build.

This means that our module specification would now work with command "new". We
add "ALARM:R3-8" and "MISC_DBC:R3-0" to the file sumo-build.config at key
"module" and can then create a build with::

  sumo-build new


