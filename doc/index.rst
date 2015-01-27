.. Support Module Tools documentation master file, created by
   sphinx-quickstart on Thu Dec 19 13:05:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: logo_hzb_big.png
   :align: right
   :target: http://www.helmholtz-berlin.de

==========================================================
Welcome to SUMO documentation!
==========================================================
A SUpport MOdule manager for EPICS
----------------------------------

The support module manager is a collection of python scripts to help with the
development of EPICS applications and EPICS support modules.

Some of the program features are:

- All module dependencies are held in a `JSON <http://www.json.org>`_
  dependency database.

- A scanner program can create a dependency database from an EPICS support
  directory to help migration.

- The program builds of consistent sets of EPICS support modules.

- The program fetches module sources from URLS with tar files or a version
  control system (currently git, mercurial or darcs).
  
- RELEASE files for applications are automatically created to use support
  modules that are consistent with each other.

See :doc:`introduction` for more information.

:Author: Goetz Pfeiffer <Goetz.Pfeiffer@helmholtz-berlin.de>

Contents:

.. toctree::
   :maxdepth: 1

   sumo-install
   introduction
   modulespecs
   configuration-files
   reference-sumo-scan
   reference-sumo
   examples
   glossary

License
=======

This software of this project can be used unter the HZB :doc:`license`.

Download
========

You can download packages of the software here:

* `latest version, tar.gz file <http://www-csr.bessy.de/control/sumo/sumo-dist/sumo.tar.gz>`_
* `latest version, zip file <http://www-csr.bessy.de/control/sumo/sumo-dist/sumo.zip>`_
* `older versions <http://www-csr.bessy.de/control/sumo/sumo-dist>`_

Install
=======

Sumo uses `Python Distutils <https://docs.python.org/2/distutils>`_ for
installation. 

You find more details on how to install sumo at
:doc:`sumo-install`.

The source
==========

You can browse our `repository
<http://www-csr.bessy.de/cgi-bin/hgweb.cgi/sumo>`_ or clone it
with::

  hg clone http://www-csr.bessy.de/cgi-bin/hgweb.cgi/sumo

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

