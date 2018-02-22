.. Support Module Tools documentation master file, created by
   sphinx-quickstart on Thu Dec 19 13:05:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: logo_hzb_big.png
   :align: right
   :target: http://www.helmholtz-berlin.de

==========================================================
Welcome to EPICS-sumo documentation!
==========================================================

A SUpport MOdule manager for EPICS
==================================

The support module manager sumo is a program to build consistent sets of 
`EPICS <http://www.aps.anl.gov/epics>`_ support modules and use them in 
`EPICS <http://www.aps.anl.gov/epics>`_ applications.

Some of the features are:

- All module dependencies are held in a `JSON <http://www.json.org>`_
  dependency database.

- The dependency database can be managed automatically with a version control
  system in order to keep it in sync on a number of build hosts.

- In order to migrate your existing support module installation a scanner
  program creates a dependency database from existing support directories.

- The program builds consistent sets of 
  `EPICS <http://www.aps.anl.gov/epics>`_ support modules.

- The program fetches module source code from various sources, directories, tar
  files or version control systems (currently git, mercurial, darcs, subversion
  and cvs).
  
- If a set of support modules is to be used in an application a RELEASE is
  generated with all the relevant paths.

See :doc:`introduction` for more information.

:Author: Goetz Pfeiffer <Goetz.Pfeiffer@helmholtz-berlin.de>

Documentation
=============

Reference documents
-------------------

- :doc:`reference-sumo`
- :doc:`reference-sumo-scan`
- :doc:`configuration-files`
- :doc:`modulespecs`

Use cases
---------

- :doc:`app-usage`
- :doc:`example-sumo-build-try`
- :doc:`dev-usage`
- :doc:`migration-examples`

Full list of documents
----------------------

.. toctree::
   :maxdepth: 1

   sumo-install
   introduction
   modulespecs
   configuration-files
   reference-sumo-scan
   reference-sumo
   app-usage
   dev-usage
   example-sumo-build-try
   migration-examples
   glossary

License and copyright
=====================

Copyright (c) 2015 by `Helmholtz-Zentrum Berlin <https://www.helmholtz-berlin.de>`_.

This software of this project can be used under GPL v.3, see :doc:`license`.

Download
========

Sumo is available as a debian or rpm package, as tar.gz or zip file:

* `sumo download page <https://sourceforge.net/projects/epics-sumo/files/?source=navbar>`_
* `debian 7 packages <https://sourceforge.net/projects/epics-sumo/files/debian-7>`_
* `debian 8 packages <https://sourceforge.net/projects/epics-sumo/files/debian-8>`_
* `debian 9 packages <https://sourceforge.net/projects/epics-sumo/files/debian-9>`_
* `fedora 25 packages <https://sourceforge.net/projects/epics-sumo/files/fedora-21>`_
* `fedora 26 packages <https://sourceforge.net/projects/epics-sumo/files/fedora-22>`_
* `fedora 27 packages <https://sourceforge.net/projects/epics-sumo/files/fedora-23>`_
* `latest version, tar.gz file <http://downloads.sourceforge.net/project/epics-sumo/sumo.tar.gz>`_
* `latest version, zip file <http://downloads.sourceforge.net/project/epics-sumo/sumo.zip>`_

Install
=======

You install sumo either as a debian or rpm package with your package manager or
from source.

For details on how to install sumo see :doc:`sumo-install`.

Sumo at sourceforge
===================

You find the sourceforge summary page for sumo at
`EPICS-sumo <https://sourceforge.net/projects/epics-sumo>`_.


The source
==========

In order to browse the mercurial repository click on
`repository <https://sourceforge.net/p/epics-sumo/mercurial/ci/default/tree/>`_.

or clone it with this command::

  hg clone ssh://goetzpf@hg.code.sf.net/p/epics-sumo/mercurial sumo

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

