Introduction
============

The problem
-----------

When you develop an application for EPICS you usually need some of the EPICS
support modules. 

For a a small project you fetch the sources for support modules your
application needs and build them all together with your application.

For development in a large team however, you want to have support modules built
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

A set of modules that are consistent with respect to their versions and
dependencies is called a *build*. They all have the same *buildtag*. A makefile
is generated for each build to call the makefiles of all the modules in the
right order.

The module dependency information and the information on build are kept in
database files, which are ASCII files.

Dependencies and module versions have *states* of maturity. We distinguish three states:

stable
  These modules and builds can be build and do not have major errors e.g.
  crashing the IOC. However, there may be less serious problems or bugs.

testing
  These modules and dependent modules can be build but have not yet been tested
  in an application.

unstable
  It is not guaranteed that these modules work or can even be built. If it is
  ensured that the build process works without errors, the status should be set
  to "testing".

The implementation
------------------

The functions described above are implemented with a small set of python
scripts. The dependency and build database files are in 
`JSON <http://www.json.org>`_ format.

You can scan an existing directory with support modules to extract the
dependency information from RELEASE files there and create a dependency
database file. Since this file is an ASCII file it can easily be edited if
there is the need for corrections.

There are three scripts:

:doc:`sumo-scan <reference-sumo-scan>`
  This script is used to scan an existing support module tree for module
  versions and their repository sources. It generates a *scan* file which can
  be converted to a *DB* file withe the sumo-db script.

:doc:`sumo-db <reference-sumo-db>`
  This script manages the *DB* files with all the module version and dependency
  information. It also can also generate *partial DB* files that are used to
  create a new build.

:doc:`sumo-build <reference-sumo-build>`
  This script creates and manages builds. It also updates the *status* of
  dependencies in the *DB* file.

