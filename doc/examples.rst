Examples
========

Here are some examples of the application of *sumo*. These examples are for our
EPICS environment here at the HZB but could be applied at other sites with some
changes.

Create a dependency database with sumo-scan
-------------------------------------------

You first have to create a file sumo-scan.config with this content::

  {
      "darcs_dirtest": true,
      "dir": [
          "/opt/csr/Epics/R3.14.12/base/3-14-12-2-1",
          "/opt/Epics/R3.14.12/support"
      ],
      "exclude_deps": "home/",
      "exclude_path": [
          "apps/crateCtrl/XXXXX",
          "busy/vendor",
          "monoapps",
          "std/vendor",
          "devIocStats/vendor"
      ],
      "group_basedir": [
          "/opt/Epics/R3.14.12/support",
          "/opt/Epics/R3.14.12"
      ],
      "hint": [
      ],
      "ignore_name": [
          "TOP",
          "EPICS_SUPPORT",
          "SUPPORT",
          "TEMPLATE_TOP",
          "EPICS_SITE_TOP",
          "EPICS_MODULES",
          "MSI"
      ],
      "missing_repo": null,
      "missing_tag": null,
      "progress": true,
      "source_patch": [
          "r\"^([^:]*)$\",r\"rcsadm@aragon.acc.bessy.de:\\1\"",
          "r\"^([^@]*)$\",r\"rcsadm@\\1\"",
          "r\"\\b(aragon)(?:|\\.acc):\",r\"\\1.acc.bessy.de:\"",
          "r\"^rcsadm@localhost:\",r\"rcsadm@aragon.acc.bessy.de:\"",
          "\":darcs-repos\",\":/opt/repositories/controls/darcs\"",
          "r\"/(srv|opt)/csr/(repositories/controls/darcs)\",r\"/opt/\\2\"",
          "r\"/srv/csr/Epics\",\"/opt/Epics\""
      ],
      "verbose": null
  }

Now you can create SCAN file like this::

  sumo-scan all > SCAN.DB

The scan file is converted to a dependency database like this::

  sumo-db -P "r\"^/srv/csr/Epics\",r\"rcsadm@aragon.acc.bessy.de:/opt/Epics\"" convert stable SCAN.DB > DEPS.DB

We have to set a weight factor for our BESSYRULES module, this ensures that
this module always comes first in generated RELEASE files::

  sumo-db --db DEPS.DB --savedb weight -- -1 BESSYRULES

Set up a support directory
--------------------------

Place sumo files
++++++++++++++++

Change to your support directory. Copy the dependency database file, e.g.
"DEPS.DB" there.

For convenience, we remember the support directory in an environment variable::

  SUMODIR=`pwd`

Create a configuration file for sumo-db::

  sumo-db --maxstate stable --db $SUMODIR/DEPS.DB makeconfig

Create a configuration file for sumo-build::

  sumo-build --db $SUMODIR/DEPS.DB --builddb $SUMODIR/BUILDS.DB --supportdir $SUMODIR makeconfig

Build the EPICS base
++++++++++++++++++++

First we look what versions of the EPICS base we have::

  sumo-db showall BASE

The command gives this result::

  {
      "BASE": [
          "TAGLESS-3-14-12-2-1"
      ]
  }

We decide to build version "TAGLESS-3-14-12-2-1" of the EPICS base. We give the
new :term:`build` the :term:`buildtag` "BASE-3-14-12-2-1"::

  sumo-db --nolock distribution BASE:TAGLESS-3-14-12-2-1 | sumo-build --partialdb - new BASE-3-14-12-2-1
  make -sj -f Makefile-BASE-3-14-12-2-1

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
:term:`modulespecs`:: from file "MODULES"::

  sumo-db --maxstate stable --db $SUMODIR/DEPS.DB --update-config MODULES makeconfig

Here we create a configuration file for sumo-build that contains the
:term:`modulespecs` and :term:`aliases` from file "MODULES" ::

  sumo-build --db $SUMODIR/DEPS.DB --builddb $SUMODIR/BUILDS.DB --supportdir $SUMODIR --readonly --update-config MODULES makeconfig

Create a build for an application
---------------------------------

Now we try to use modules from our support directory::

  sumo-build useauto > configure/RELASE

The program prints this message::

  no build found that matches modulespecs

The reason is that we don't yet have built the :term:`modules` the application
needs.

So we first have to create a new build. 

We remember our application directory in an environment variable::

  APPDIR=`pwd`

Now we go the the support directory::

  cd $SUMODIR

We assume that the name of our :term:`build` should be "MLS-01"::

  sumo-db --nolock --update-config $APPDIR/sumo-db.config distribution | sumo-build --partialdb - new MLS-01

The first part of the command line creates a definition of all :term:`modules`
in form of a :term:`partialdb`. We do not save this as a file but pass it
directly to sumo-build. sumo-build checks out the sources of all additional
:term:`modules` needed, creates a new entry in the :term:`builddb` database and
creates a makefile.

Now we compile the :term:`build`::

  make -sj -f Makefile-MLS-01

After a successful build, we mark the :term:`build` with 
:term:`state` "stable"::

  sumo-build state MLS-01 stable

Use a build in an application
-----------------------------

We first go back to the application directory::

  cd $APPDIR

We use command "useauto" which combines "find" and "use". It looks in the
:term:`support directory` for a :term:`build` matching our requirements and
creates a RELEASE file that uses that :term:`build`::

  sumo-build useauto > configure/RELASE

For our information the program shows on standard error what build was used. 

Now that the RELEASE file is created we can go ahead and build our application
by calling "make"::

  make

