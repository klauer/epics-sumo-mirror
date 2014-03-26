sumo-build
==========

What the script does
--------------------

This script creates and manages builds and updates the *status* of
:term:`dependencies` in the :term:`DB` file.

The script takes one or mode commands and has a number of options. Single
character options always start with a single dash "-", long options start with
a double dash "--", commands are simple words on the command line.

How it works
------------

All :term:`builds` are kept in a single directory, the :term:`support directory`. Information in :term:`builds` is kept in a `JSON <http://www.json.org>`_ file, the build database or :term:`BUILDDB`.

The build database
++++++++++++++++++

The build database or :term:`BUILDDB` file is a `JSON <http://www.json.org>`_
file that contains information all :term:`builds` in the 
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

This is a :term:`state` string that describes the state of the :term:`build`. Here are the meanings of the :term:`state` string:

* unstable: the :term:`build` has been created, not yet compiled
* testing: the :term:`build` has been compiled successfully
* stable: the :term:`build` has been used in production successfully


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

new [BUILDTAG]
++++++++++++++

This command creates a new build. It must be followed by a :term:`buildtag`. Note that options "--db", --partialdb" and "--builddb" are mandatory for this command.

partialdb [BUILDTAG]
++++++++++++++++++++

This command recreates a :term:`partialdb` from a complete :term:`DB` and a
:term:`build`. The :term:`partialdb` is printed on the console.

find [MODULESPECS]
++++++++++++++++++

This command is used to find matching :term:`builds` for a given list of
:term:`modulespecs`. It prints a list of :term:`buildtags` of matching
:term:`builds` on the console. Note that the :term:`versions` in
:term:`modulespecs` may be *unspecified*, *specified exactly* or 
*specifed by relation*.

useall [BUILDTAG]
+++++++++++++++++

This command creates a RELEASE file for an application. The command must be
followed by :term:`buildtag`. The release file is created that it includes
*all* :term:`modules` of the build.

use [BUILDTAG] [MODULES]
++++++++++++++++++++++++

This command creates a RELEASE file for an application. The command must be
followed by a :term:`buildtag` and a list of :term:`modulespecs`. The RELEASE
created includes only the modules that are specified. For this command the
:term:`DB` file must be specified with the "--db" option.

list
++++

This command lists the names of all builds.

show [BUILDTAG]
+++++++++++++++

This command shows the data of a build. It must be followed by a
:term:`buildtag`. 

state [BUILDTAG] {NEW STATE}
++++++++++++++++++++++++++++

This command is used to show or change the state of a build. If must be
followed by a :term:`buildtag`. If there is no new :term:`state` given, it just
shows the current :term:`state` of the :term:`build`. Otherwise the
:term:`state` of the :term:`build` is changed to the given value. 

delete [BUILDTAG]
+++++++++++++++++

If no other :term:`build` depends on the :term:`build` specified by the
:term:`buildtag`, the directories of the :term:`build` are removed and it's
entry in the :term:`builddb` is deleted.

cleanup [BUILDTAG]
++++++++++++++++++

This command removes the remains of a failed :term:`build`. If the command
"new" is interrupted or stopped by an exception in the program, the
:term:`build` may be in an incomplete state. In this case you can use the
"cleanup" command to remove the directories of the failed build.
