Examples
========

Here are some examples of the application of *sumo*. These examples are for our
EPICS environment here at the HZB but could be applied at other sites with some
changes.

Migrating
---------

This chapter shows how to *migrate* your existing installation of support
modules to sumo. sumo-scan can help you to create a first version of the
dependency database. Alternatively you can create the dependency database from
scratch.

Create the sumo directory
+++++++++++++++++++++++++

We create a directory which will hold all sumo files and remember it in an environment variable::

  cd <my sumo directory>
  SUMODIR=`pwd`
  mkdir scan database build

Create a dependency database with sumo-scan
+++++++++++++++++++++++++++++++++++++++++++

In our sumo directory we create a configuration file "sumo-scan.config" with
this content::

  {
      "dir": [
          "/opt/csr/Epics/R3.14.12/base/3-14-12-2-1",
          "/opt/Epics/R3.14.12/support"
      ],
      "exclude-deps": "home/",
      "exclude-path": [
          "apps/crateCtrl/XXXXX",
          "busy/vendor",
          "monoapps",
          "std/vendor",
          "devIocStats/vendor"
      ],
      "group-basedir": [
          "/opt/Epics/R3.14.12/support",
          "/opt/Epics/R3.14.12"
      ],
      "hint": [
      ],
      "ignore-name": [
          "TOP",
          "EPICS_SUPPORT",
          "SUPPORT",
          "TEMPLATE_TOP",
          "EPICS_SITE_TOP",
          "EPICS_MODULES",
          "MSI"
      ],
      "progress": true,
      "url-patch": [
          "r\"^([^:]*)$\",r\"rcsadm@aragon.acc.bessy.de:\\1\"",
          "r\"^([^@]*)$\",r\"rcsadm@\\1\"",
          "r\"\\b(aragon)(?:|\\.acc):\",r\"\\1.acc.bessy.de:\"",
          "r\"^rcsadm@localhost:\",r\"rcsadm@aragon.acc.bessy.de:\"",
          "\":darcs-repos\",\":/opt/repositories/controls/darcs\"",
          "r\"/(srv|opt)/csr/(repositories/controls/darcs)\",r\"/opt/\\2\"",
          "r\"/srv/csr/Epics\",\"/opt/Epics\""
      ],
      "dir-patch": [
          "r\"/(srv|opt)/csr/(repositories/controls/darcs)\",r\"/opt/\\2\"",
          "r\"/srv/csr/Epics\",\"/opt/Epics\""
      ]
  }

Now we run sumo-scan and create a *SCAN* file::

  sumo-scan all > scan/SCAN

We now have the results of the scan in a single file. This file is in 
`JSON <http://www.json.org>`_ format, you may load this file with your
text editor or even modify it.

The scan file is now converted to a dependency database and a scan database
like this::

  sumo db -U "r\"^/srv/csr/Epics\",r\"rcsadm@aragon.acc.bessy.de:/opt/Epics\"" --db database/DEPS.DB --scandb database/SCAN.DB convert scan/SCAN

We have to set a weight factor for our BESSYRULES module, this ensures that
this module always comes first in generated RELEASE files::

  sumo db --db database/DEPS.DB weight -- -1 BESSYRULES

Create the sumo configuration file
++++++++++++++++++++++++++++++++++

We create a sumo configuration file with this command::

  sumo makeconfig sumo.config --builddir $SUMODIR/build --db $SUMODIR/database/DEPS.DB --scandb $SUMODIR/database/SCAN.DB

Using sumo for the first time
-----------------------------

If the sumo directory, the dependency database and the sumo configuration file
are set up, we can now use sumo to build an EPICS base.

Build the EPICS base
++++++++++++++++++++

First we look what versions of the EPICS base we have::

  sumo db show BASE

In our example, the command gives this result::

  {
      "BASE": [
          "R3-14-12-2-1"
      ]
  }

We decide to :term:`build` version "R3-14-12-2-1" of the EPICS base. We use
buildtag stem "BASE" in order to make the name of the build indicate what it
contains::

  sumo build --buildtag-stem BASE new BASE:R3-14-12-2-1

We now see what builds are there::

  sumo build list

The displayed text is::

  BASE-001

The details of the build we see with this command::

  sumo build show BASE-001

which returns::

  {
      "BASE-001": {
          "modules": {
              "BASE": "R3-14-12-2-1"
          },
          "state": "testing"
      }
  }

Convert an application to SUMO
------------------------------

In our example we assume that you have our application "MLS-Controls" checked
out. We first change the directory::

  cd <my MLS-Controls directory>

Create configuration file and module list
+++++++++++++++++++++++++++++++++++++++++

We first have to scan the existing RELEASE file with sumo-scan. We have to
know the paths of our old EPICS base and the old support directory, these are
given as option "-g" to the program. Option "-N" gets a list of variable names
in the RELEASE file that should be ignored. The output of sumo-scan is directed
to sumo which creates a `JSON <http://www.json.org>`_ file with
:term:`modulespecs` and :term:`aliases`::

  sumo-scan -d . all -g '/opt/csr/Epics/R3.14.12/support /opt/csr/Epics/R3.14.12' -N 'TOP EPICS_SUPPORT SUPPORT TEMPLATE_TOP EPICS_SITE_TOP EPICS_MODULES MSI' | sumo db appconvert - -C > configure/MODULES

Now we create a configuration file for sumo db that contains the list of
:term:`modulespecs` from file "MODULES"::

  sumo -C --scandb $SUMODIR/database/SCAN.DB --db $SUMODIR/database/DEPS.DB --builddir $SUMODIR/build --#preload configure/MODULES --buildtag-stem MLS makeconfig sumo.config

Build all support modules the application requires
++++++++++++++++++++++++++++++++++++++++++++++++++

Now we try to use modules from our support directory::

  sumo build use

The program prints this message::

  no build found that matches modulespecs

The reason is that we don't yet have built the :term:`modules` the application
needs.

So we first have to create a new build::

  sumo build new

This command shows the following error message::

  error: set of modules is incomplete, these modules are missing: MISC_DBC MISC_DEBUGMSG
  
We use "try" to investigate the problem::

  sumo build try --detail 1

We see what modules are missing an a suggestion on possible versions to use. We add on the command line the missing modules::

  sumo build try -A module MISC_DBC:R3-0 MISC_DEBUGMSG:R3-0

Sumo replies::

  Your module specifications are complete. You can use these with command 'new'
  to create a new build.
  
We first add the two modules to the file configure/MODULES. You could use a text editor for this or you can use this sumo command line::

  sumo -A module -m 'MISC_DBC:R3-0 MISC_DEBUGMSG:R3-0' makeconfig configure/MODULES alias module

Now we can create the build::

  sumo build new

The list of :term:`modules` is taken from file $APPDIR/configure/MODULES. The
program creates a collection of all :term:`modules` needed, checks out the
sources of all :term:`modules`, creates a new entry in the :term:`builddb`
database, creates a makefile and calls make.

Use the support modules in the application
++++++++++++++++++++++++++++++++++++++++++

After all needed support modules were built (see above) we create a new file
configure/RELEASE with::

  sumo build use

The sumo command "build use" looks in the :term:`support directory` for 
a :term:`build` matching our :term:`module` requirements and creates
a RELEASE that uses that :term:`build`. The program responds::

  using build MLS-01
  
Now that the RELEASE file is created we can go ahead and build our application
by calling "make"::

  make

