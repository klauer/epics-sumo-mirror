Introduction
============

The following text provides a short introduction of the tool.

If you want to get an impression how you use sumo in an application look at
:doc:`Using sumo in your application <app-usage>`.

If you want to get an impression how to change and develop a device support with sumo look at
:doc:`Develop support modules with sumo <dev-usage>`.

The problem
-----------

When you develop EPICS applications you usually need some EPICS support
modules to interface your hardware. 

For a a small project you fetch the sources for support modules your
application needs and build them along with your application.

For development in a team however, you need to have support modules built and
installed at a central directory so all developers can just use them instead of
building them again and again.

If new versions of your support modules with bug fixes or new features become
available, you have to build these in order to use them. The old versions
however, must not be deleted since some applications may depend on them. This
is further complicated by the fact that support modules may be dependent on
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
behave differently which could break existing applications. So you have to create
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

- Creation of a new application: You probably know what modules your
  application needs, but what versions should you use ? What set of module
  versions is consistent with each other with respect to module dependencies ?
  Currently you copy a RELEASE file of another application and try to modify it
  in a trial and error fashion.
  
The solution
------------

A solution of these problems is to create RELEASE files with a tool instead of
keeping them under version control. In your version control system you just
have a *template* of a RELEASE file that gives hints on what other modules your
module depends on.

Module versions and module dependencies are kept in a dependency database. 

Sets of modules that are *complete* and *consistent* are created by a tool. The
tool creates a makefile for each set that ensures that modules are compiled in
the right order. Every set, which is also called a :term:`build`, is identified
by a unique name, a :term:`buildtag`. Information on builds is stored in a
build database or :term:`BUILDDB`.

Modules reside in directories whose names contain the :term:`module`
:term:`version` tag and the :term:`buildtag`. A :term:`module` of the same
version may exist in different :term:`builds` with with different versions of
dependency versions.

Some versions of :term:`modules` may be part of more than one :term:`build` in
order to reduce compile time and optimize disk space. The tool ensures that all
:term:`builds` are still consistent and complete.

Databases are always files in `JSON <http://www.json.org>`_ format.

The concept of states
---------------------

In order to distinguish the maturity of :term:`builds` we distinguish the
following :term:`build` :term:`states`:

stable
  Stable means that the :term:`build` is used in production and is not known to
  have major faults.

testing
  Testing means that the :term:`build` could be compiled without errors. If it
  is used on an IOC for some time without major problems, the :term:`build`
  :term:`state` should be set to "stable".

unstable
  Unstable means that the :term:`build` is just created. This is also the state
  of a build if it's compilation fails.

disabled
  The build should no longer be used, it has a defect or cannot be recreated
  due to changes in the dependency database.

The implementation
------------------

The functions described above are implemented with two programs. The
dependency and build database files have `JSON <http://www.json.org>`_ format.

Here are two programs:

:doc:`sumo-scan <reference-sumo-scan>`
  This is a python script that is used to scan an existing support module tree
  for module versions and their repository sources. It generates a *scan* file
  which can be converted to a *DB* file with `sumo <reference-sumo>`.

:doc:`sumo <reference-sumo>`
  This python script manages *DB* files that hold all module version and
  dependency information and creates and manages builds.
