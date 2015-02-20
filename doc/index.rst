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

The support module manager sumo is a program to build consistent sets of EPICS
support modules and use them in EPICS applications.

Some of the features are:

- All module dependencies are held in a `JSON <http://www.json.org>`_
  dependency database.

- In order to migrate your existing support module installation a scanner
  program creates a dependency database from existing support directories.

- The program builds consistent sets of EPICS support modules.

- The program fetches module source code from various sources, directories, tar
  files or version control systems (currently git, mercurial or darcs).
  
- If a set of support modules is to be used in an application a RELEASE is
  generated with all the relevant paths.

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
   app-usage
   examples
   glossary

License
=======

This software of this project can be used unter the GPL v.3, see :doc:`license`.

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

