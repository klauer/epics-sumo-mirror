Introduction
============

The problem
-----------

When you develop an application for EPICS you usually need some of the EPICS
support modules. 

For a a small project you have to fetch the sources for all support modules your
application needs and build all of them together with your application.

For development in a team however, you want to have support modules built
and installed at a central directory so all developers can just use them in their
application without the need to build them again for each application.

Support modules are also developed and to use new features, you have to install
new versions.  Soon you different versions of many modules. Some older
applications may rely on older module versions while others may need newer
ones.  This is further complicated by the fact that modules may be dependent on
each other. 

Here is an example, module "A" is dependent on module "B":

==================   ================   ==============================
module A directory   module A version   built against module B version
==================   ================   ==============================
support/A/R1.3       1.3                2.4
support/A/R1.4       1.4                2.4
==================   ================   ==============================

Now suppose that there is a new version "2.5" of "B". You want to build "A"
against that version of "B" while the source code of "A" has not
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

For each module that like "A" uses "B" you have to create a new directory with a
new version number and rebuild the module. 

These are the problems with this approach:

- Changes in the support directory: If you want to install a new version of a
  module you have to look at the RELEASE files of all other modules in order to
  find which modules depend on this one.  All of these have to be rebuild in a
  new directory. In all these cases you have to patch the RELEASE file with the
  path of the new module version. If the RELEASE file is under version control
  you even have to commit these changes and give it a release tag (at least in
  darcs VCS).

- Creating a new application: You probably know what modules your application
  needs, but what versions should you use ? What set of module versions is
  consistent with each other with respect to module dependencies ? Currently
  you copy a RELEASE file of another application and try to modify it in a
  trial and error fashion.
  
The solution
------------

The solution of these problems is to create RELEASE files with tools instead of
keeping them under version control. In your version control system you just
have a *template* of a RELEASE file that gives hints on what modules you depend
on.

Information on module versions and module dependencies is held in a dependency
database. 

Sets of modules that are *complete* and *consistent* are created by a tool. The
tool creates a makefile for each set that ensures that modules are compiled in
the right order. Every set, which is also called a *build*, is identified by a
unique name, a *buildtag*. Information on builds is stored in a build database.

Modules reside in directories whose names contain the module version tag and
the buildtag. A module of the same version may exist in different builds with
with different versions of dependency versions.

Some versions of modules may be part of more than one build in order to reduce
compile time and optimize disk space. The tool ensures that all builds are
still consistent and complete.

Databases are always files in `JSON <http://www.json.org>`_ format.

The concept of states
---------------------

In order to distinguish the maturity of modules, dependencies and builds we
distinguish 3 different states:

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

Modules can be built for several target architectures. Each module version in
the dependency database has a list of supported target architectures. Modules
that are independent of an architecture have the special architecture "ANY" in
their list. 

The implementation
------------------

The functions described above are implemented with three programs.  The
dependency and build database files have `JSON <http://www.json.org>`_ format.

Here are three programs:

:doc:`sumo-scan <reference-sumo-scan>`
  This is a python script that is used to scan an existing support module tree
  for module versions and their repository sources. It generates a *scan* file
  which can be converted to a *DB* file with the `sumo-db <reference-sumo-db>`.

:doc:`sumo-db <reference-sumo-db>`
  This python script manages *DB* files that hold all module version and
  dependency information. 

:doc:`sumo-build <reference-sumo-build>`
  This python script creates and manages builds. It also updates the *status*
  of dependencies in the *DB* file.

