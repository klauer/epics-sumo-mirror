Examples
========

Here are some examples of the application of *sumo*. These examples are for our
EPICS environment here at the HZB but could be applied at other sites with some
changes.

Create a dependency database with sumo-scan
-------------------------------------------

You first have to create a file sumo-scan.config with this content::

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

Now you can create SCAN file like this::

  sumo-scan all > SCAN

The scan file is converted to a dependency database and a scan database like
this::

  sumo-db -P "r\"^/srv/csr/Epics\",r\"rcsadm@aragon.acc.bessy.de:/opt/Epics\"" --db DEPS.DB --scandb SCAN.DB convert SCAN

We have to set a weight factor for our BESSYRULES module, this ensures that
this module always comes first in generated RELEASE files::

  sumo-db --db DEPS.DB weight -- -1 BESSYRULES

Set up a support directory
--------------------------

Place sumo files
++++++++++++++++

Change to your support directory. Copy the dependency database file, e.g.
"DEPS.DB" there.

For convenience, we remember the support directory in an environment variable::

  SUMODIR=`pwd`

Create a configuration file for sumo-db::

  sumo-db --scandb $SUMODIR/SCAN.DB --db $SUMODIR/DEPS.DB makeconfig

Create a configuration file for sumo-build::

  sumo-build --scandb $SUMODIR/SCAN.DB --db $SUMODIR/DEPS.DB --builddir $SUMODIR --makeopts "-s" makeconfig

Build the EPICS base
++++++++++++++++++++

First we look what versions of the EPICS base we have::

  sumo-db showall BASE

The command gives this result::

  {
      "BASE": [
          "R3-14-12-2-1"
      ]
  }

We decide to build version "R3-14-12-2-1" of the EPICS base. We give the
new :term:`build` the :term:`buildtag` "BASE-3-14-12-2-1"::

  sumo-build --buildtag BASE-3-14-12-2-1 new BASE:R3-14-12-2-1

After a successful build we mark the :term:`build` with :term:`state` "stable"::

  sumo-build state BASE-3-14-12-2-1 stable

Prepare an application for SUMO use
-----------------------------------

In our example we assume that you have our application "MLS-Controls" checked
out. We first have to scan the existing RELEASE file with sumo-scan. We have to
know the paths of our old EPICS base and the old support directory, these are
given as option "-g" to the program. Option "-N" gets a list of variable names
in the RELEASE file that should be ignored. The output of sumo-scan is directed
to sumo-db which creates a `JSON <http://www.json.org>`_ file with
:term:`modulespecs` and :term:`aliases`::

  sumo-scan -d . all -g '/opt/csr/Epics/R3.14.12/support /opt/csr/Epics/R3.14.12' -N 'TOP EPICS_SUPPORT SUPPORT TEMPLATE_TOP EPICS_SITE_TOP EPICS_MODULES MSI' | sumo-db appconvert - > MODULES

Now we create a configuration file for sumo-db that contains the list of
:term:`modulespecs` from file "MODULES"::

  sumo-db --scandb $SUMODIR/SCAN.DB --db $SUMODIR/DEPS.DB -c MODULES makeconfig

Here we create a configuration file for sumo-build that contains the
:term:`modulespecs` and :term:`aliases` from file "MODULES" ::

  sumo-build --db $SUMODIR/DEPS.DB --builddir $SUMODIR -c MODULES makeconfig

Create a build for an application
---------------------------------

Now we try to use modules from our support directory::

  sumo-build use

The program prints this message::

  no build found that matches modulespecs

The reason is that we don't yet have built the :term:`modules` the application
needs.

So we first have to create a new build. 

We assume that the name of our :term:`build` should be "MLS-01"::

  sumo-build --buildtag MLS-01 new

This command shows the following error message::

  error: set of modules is incomplete, these modules are missing: MISC_DBC MISC_DEBUGMSG
  
We use "try" to investigate the problem::

  sumo-build --buildtag MLS-01 try 

We see at the start of the rather long report that this shows too, that the
two modules are missing. We add them on the command line and use again "try"::

  sumo-build --buildtag MLS-01 try MISC_DBC MISC_DEBUGMSG | less

At the start of the report we see::

  Not all modules have exactly specified versions. These modules need an 
  exact version specification:
      MISC_DBC             -> suggested version: R3-0
      MISC_DEBUGMSG        -> suggested version: R3-0

So we add "MISC_DBC:R3-0" and "MISC_DEBUGMSG:R3-0" to the list of modules in
file $APPDIR/sumo-build.config, open the file in any text editor and add these
lines at key "module"::

  "MISC_DBC:R3-0",
  "MISC_DEBUGMSG:R3-0",

We check the result with command "try"::

  sumo-build --buildtag MLS-01 try 

At the end of the report we see::

  Your module specifications are complete. You can use these with command
  'new' to create a new build.
  
Now we can create the build::

  sumo-build --buildtag MLS-01 new

The list of :term:`modules` is taken from file $APPDIR/sumo-build.config. The
program creates a collection of all :term:`modules` needed, checks out the
sources of all :term:`modules`, creates a new entry in the :term:`builddb`
database, creates a makefile and calls make.

After a successful build, we mark the :term:`build` with 
:term:`state` "stable"::

  sumo-build state MLS-01 stable

Use a build in an application
-----------------------------

We assume that we are in our application directory.

The sumo-build command "use" looks in the :term:`support directory` for 
a :term:`build` matching our :term:`module` requirements and creates
a RELEASE that uses that :term:`build`::

  sumo-build use 

The program responds::

  using build MLS-01
  
Now that the RELEASE file is created we can go ahead and build our application
by calling "make"::

  make

