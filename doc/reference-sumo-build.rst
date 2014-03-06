sumo-build
==========

What the script does
--------------------

This script creates and manages builds and updates the *status* of dependencies
in the *DB* file.

The script takes one or mode commands and has a number of options. Options
always start with a dash "-", commands are simple words.

Commands
--------

edit
++++

Start the editor specified by the environment variable "VISUAL" or "EDITOR"
with that file. This command first aquires a file-lock on the file that is only
released when the editor program is terminated.  If you want to edit a DB or
BUILDDB file directly, you should always do this with this command. The file
locking prevents other users to use the file at the same time you modify it.

This command must be followed by a *filename*.

new
+++

This command creates a new buildtree. It must be followed by a *buildtag*, a
unique name that identifies the build.

partialdb
+++++++++

This command is used to recreate a *partialdb* from a complete *db* and a buildtree.

find
++++

This command is used to find matching buildtrees for a given list of module specs which must follow this command. 

module spec
:::::::::::

A *module spec* is a string "modulename" or "modulename:versionspec". A
*modulename* is a unique name that identifies the module. *versionspec* can
have one of three forms:

version
  This means that we want exactly that version, as in "MCAN:2-3-13".

-version
  This means that we want that version or a smaller version, e.g.
  "MCAN:-2-3-13" would match version 2-3-12 and 2-3-13 but not version 2-3-14.

-version
  This means that we want that version or a greater version, e.g.
  "MCAN:+2-3-13" would match version 2-3-13 and 2-3-14 but not version 2-3-12.

useall
++++++

This command creates a RELEASE file for an application. The command must be
followed by *buildtag*. The release file is created that it includes *all*
modules of the build.

use
+++

This command creates a RELEASE file for an application. The command must be
followed by a *buildtag* and a list of *module specs*. The RELEASE is created
that it includes only the modules that are specified. For this command the
database file must be specified with the "--db" option.

list
++++

List the names of all builds.

show
++++

This command shows the data of a build. It must be folloed by a *buildtag*. 

state
+++++

This command is used to show or change the state of a build. If must be
followed by a *buildtag*. If there is no new state given, it just shows the
current state of the build. Otherwise the state of the build is changed to the
given value. 

delete
++++++

This command removes a build from the disk and marks it in the build database
as "deleted".
