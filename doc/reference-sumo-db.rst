sumo-db
=======

What the script does
--------------------

This script manages the depencency database or *DB* file. It is used to create
this file from the output of :doc:`sumo-scan <reference-sumo-scan>`, to change
this file and to create a *partialdb* file that is used by the
:doc:`sumo-build <reference-sumo-build>` script.

The script takes one or mode commands and has a number of options. Options
always start with a dash "-", commands are simple words.

Commands
--------

convert
+++++++

This is the command to convert the output of 
:doc:`sumo-scan all<reference-sumo-scan>` to a DB (dependency database). The
text in `JSON <http://www.json.org>`_ format is printed to the console. 

This command has two mandatory parameters:

state
:::::

This specifies the state that is assigned to all modules and dependencies in
the dependency database. These are the three allowed states:

stable
  Modules and dependencies that are known to work.

testing
  Modules and their dependencies than can be built.

unstable
  Modules and their dependencies that are just being built.

scanfile
::::::::

This is the filename with the output of 
:doc:`sumo-scan all<reference-sumo-scan>`. If you put "-" here, the script
expects the scanfile from standard input.

distribution
++++++++++++

This command creates a *distribution* from a dependency database file. A
*distribution* is a set of versioned modules that are consistent according to
the data in the dependency database. The output of this command is a 
`JSON <http://www.json.org>`_ structure that has the same format as the
dependency database. It is, in fact, a part of the dependency database where
only one version is listed for each module that is to be included in the
distribution. This is also called a *partialdb* since it is a partial
database.

The *partialdb* file is used by the script 
:doc:`sumo-build <reference-sumo-build>` to create a *build*.

This command has must be followed by at least two parameters, a *maximum state*
and at least one *module spec*. If there is more than one *module spec* they
must be separated by whitespaces.

maximum state
:::::::::::::

The *maximum state* is the maximum allowed state that a module or dependency
may have in order to be included in the distribution. As mentioned at other
places we have three possible states, "static", "testing" and "unstable". These
states have, per definition, this order relation::

  stable < testing < unstable

If you specify for example "testing" as *maximum state*, the states "stable"
and "testing" are allowed for modules and dependencies. 

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

show
++++

This command shows all modules in the dependency database. 

shownewest
++++++++++

This command shows only the newest versions of modules. It must be followed by
the parameter *maximum state* and it may be followed by a whitespace separated
list of module names. 

maximum state
:::::::::::::

The *maximum state* is the maximum allowed state that a module or dependency
may have. As mentioned at other places we have three possible states, "static",
"testing" and "unstable". These states have, per definition, this order
relation::

  stable < testing < unstable

If you specify for example "testing" as *maximum state*, the states "stable"
and "testing" are allowed for modules and dependencies. 

module name
:::::::::::

The command may be followed by one or mode module names. If given, only the
newest versions for these modules are printed to the console. If this parameter
is omitted, the newest versions for all modules are printed to the console.

showall
+++++++

This command shows all versions of modules.  It must be followed by the
parameter *maximum state* and it may be followed by a whitespace separated list
of module names. 

maximum state
:::::::::::::

The *maximum state* is the maximum allowed state that a module or dependency
may have. As mentioned at other places we have three possible states, "static",
"testing" and "unstable". These states have, per definition, this order
relation::

  stable < testing < unstable

If you specify for example "testing" as *maximum state*, the states "stable"
and "testing" are allowed for modules and dependencies. 

module name
:::::::::::

The command may be followed by one or mode module names. If given, only
versions for these modules are printed to the console. If this parameter is
omitted, versions for all modules are printed to the console.

merge
+++++

This command merges a dependency database with another dependency database. The
database that is modified must follow the command as a parameter. The database
that is added must be specified with the "--db" option.

filter
++++++

This command prints only the parts of the dependency database that contain the
given modules. The command must be followed by one or more whitespace separated
module specifications, which may contain module version numbers. If called with
option "--savedb", the db file is overwritten with the result.

cloneversion
++++++++++++

This command adds a new version for a module to the database by copying the old
version. All modules that depend on the old version now also depend on the new
version of the module. If you do this you must update the module source
definition of the new version by editing the database file directly.

replaceversion
++++++++++++++

This command replaces a version of a module with a new version. All the data of
the module is copied. All modules that used to depend on the old version now
depend on the new version.
