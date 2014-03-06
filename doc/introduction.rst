Introduction
============

The problem
-----------

When you develop an application for EPICS you usually need some of the EPICS
support modules. 

For a a small project you fetch the sources for all support modules your
application needs and build them all together with your application.

For development in a team however, you want to have support modules built
and installed at a central directory so all developers can just use them in their
application without the need to build them again.

Soon you need to have different versions of the modules. Some older
applications may rely on older module versions while others may need newer
ones.  This is further complicated by the fact that modules may be dependent on
each other. 

Here is an example, module "A" needs module "B":

==================   ================   ==============================
module A directory   module A version   built against module B version
==================   ================   ==============================
support/A/R1.3       1.3                2.4
support/A/R1.4       1.4                2.4
==================   ================   ==============================

Now suppose that there is a new version "2.5" of "B". You want to build "A"
against that version of "B", but the source code version of "A" has not
changed. You cannot rebuild in directory "support/A/R1.4" since module "A" may
behave differently which could break existing applications. So you have to make
a new directory for a new sub version of "A" like shown here:

==================   ================   ==============================
module A directory   module A version   built against module B version
==================   ================   ==============================
support/A/R1.3       1.3                2.4
support/A/R1.4       1.4                2.4
support/A/R1.3-1     1.3                2.5
support/A/R1.4-1     1.4                2.5
==================   ================   ==============================

For each module that uses module "B" you have to create a new directory with a
new version number and rebuild the module. 

With this in mind, these are the problems here:

- Installing of a new version of a module. You have to look at the RELEASE
  files of all other modules in order to find which modules depend on this one.
  All of these have to be rebuild in a new directory. In all these cases you
  have to change the RELEASE file to contain the path of the new version
  module. If the RELEASE file is under version control you even have to commit
  these changes and give it a tag (at least in darcs VCS).

- Creation of a new application. You probably know what modules your
  application needs, but what versions to use ? What set of module versions is
  consistent with each other with respect to module dependencies ? Currently
  you take an existing version and copy the file RELEASE and possibly change
  it. 

The solution
------------

The  solution is to create RELEASE files with tools instead of keeping them in
the source version control system. In your version control you just have a
*template* meaning an example for a RELEASE file that gives hints on what
modules the current module depends on.

There may be different builds of the same version of a module if one of the
modules it depends on have changed. So modules are not only distinguished by a
version number but also a build name (called *buildtag* here).

A set of modules that is consistent with respect to versions and
dependencies is called a *build*. They all have the same *buildtag*. A makefile
is generated for each build to call the makefiles of all modules in the
right order.

The module specifications and dependency information is kept in a dependency
database or DB file. Information on builds is kept in a build database or
BUILDDB file. Both files are `JSON <http://www.json.org>`_ files.

The concept of states
---------------------

In order to distinguish the maturity of modules, dependencies and builds we distinguish 3 different states:

stable
  Stable means that the item is used in production and is not known to have
  major faults.

testing
  Testing means that the item can be used on an IOC but it not yet tested. If
  it runs on an IOC for some time without major problems, the item state should
  be set to "stable".

unstable
  Unstable means that the item was just created. It is not guaranteed to work
  and is not even guaranteed that this can be booted or even compiled. It it is
  loaded and left on an IOC to run for a longer time it's state should be set
  to "testing".

The concept of architectures
----------------------------

Modules can be built for several target architectures. A list of all currently
known and supported target architectures is held the dependency database (DB)
file for each module. 

A build is always created for a single set of target architectures which is
stored in the build database (BUILDDB) file. This means that all modules in a
build are compiled for the same set of target architectures although some of
the modules may support more target architectures as it is specified in the
dependency database (DB) file.

The implementation
------------------

The functions described above are implemented with a set of python
scripts. The dependency and build database files have
`JSON <http://www.json.org>`_ format.

Here are three scripts:

:doc:`sumo-scan <reference-sumo-scan>`
  This script is used to scan an existing support module tree for module
  versions and their repository sources. It generates a *scan* file which can
  be converted to a *DB* file with the sumo-db script.

:doc:`sumo-db <reference-sumo-db>`
  This script manages the *DB* files with all the module version and dependency
  information. It also can also generate *partial DB* files that are used to
  create a new build.

:doc:`sumo-build <reference-sumo-build>`
  This script creates and manages builds. It also updates the *status* of
  dependencies in the *DB* file.

