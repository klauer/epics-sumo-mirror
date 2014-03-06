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
development of EPICS applications who use EPICS support modules.

Some of the features are:

- Keeping track of module dependencies in a `JSON <http://www.json.org>`_
  database.

- Scanning an existing EPICS support directory to create the dependency
  database.

- Creation and build of consistent sets of modules.

- Fetching module sources from a version control system.
  
- Creation of RELEASE files for applications in order to use a consistent
  module set.

See :doc:`introduction` for more information.

:Author: Goetz Pfeiffer <Goetz.Pfeiffer@helmholtz-berlin.de>

Contents:

.. toctree::
   :maxdepth: 1

   introduction
   reference-sumo-scan
   reference-sumo-db
   reference-sumo-build

License
=======

This software of this project can be used unter the HZB :doc:`license`.

Download
========

You can download packages of the software here:

* `latest version, tar.gz file <http://www-csr.bessy.de/control/sumo/sumo-dist/sumo.tar.gz>`_
* `latest version, zip file <http://www-csr.bessy.de/control/sumo/sumo-dist/sumo.zip>`_
* `older versions <http://www-csr.bessy.de/control/sumo/sumo-dist>`_

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

