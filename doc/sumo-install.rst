Installing Sumo
===============

Parts of sumo
-------------

Sumo consists of scripts, python modules, documentation and configuration
files. 

The distribution does not contain the configuration files since you have
to adapt them to your development host. Examples of configuration files are
shown further below.

Requirements
------------

Sumo requires at least `Python <https://www.python.org>`_ version 2.5 or newer.
It can also run with python 3.

Sumo is tested on `debian <https://www.debian.org>`_ and 
`Fedora <https://getfedora.org>`_ linux distributions but should run on all
linux distributions. It probably also runs on other flavours of unix, probably
even MacOS, but this is not tested.

It may run on windows, escpecially the `Cygwin <https://www.cygwin.com>`_
environment, but this is also not tested.

Packages
--------

Sumo is available as a debian or rpm package, as a tar.gz and zip file. How
sumo has to be installed depends on the package format.

Install from a debian package
+++++++++++++++++++++++++++++

There are packages for debian 7 (wheezy) and debian 8 (jessie). In order to see
what debian version you use enter::

  lsb_release -r

Simply download the debian package from 

* `debian 7 packages <https://sourceforge.net/projects/epics-sumo/files/debian-7>`_
* `debian 8 packages <https://sourceforge.net/projects/epics-sumo/files/debian-8>`_

and install with::

  dpkg -i <PACKAGENAME>

The packages may or may not work for other debian versions, but this was not
tested. As a last resort you may always install from source 
(see `Install from source (tar.gz or zip file)`_).

Note that you have to *configure* sumo after installing it, see 
`The sumo configuration file`_.

Install from a rpm package
++++++++++++++++++++++++++

There are packages for fedora 21 and fedora 22. In order to see
what fedora version you use enter::

  lsb_release -r

Simply download the rpm package from 

* `fedora 21 packages <https://sourceforge.net/projects/epics-sumo/files/fedora-21>`_
* `fedora 22 packages <https://sourceforge.net/projects/epics-sumo/files/fedora-22>`_

and install with::

  rpm -ivh  <PACKAGENAME>

The packages may or may not work for other fedora versions, redhat or
scientific linux but this was not tested. As a last resort you may always
install from source (see `Install from source (tar.gz or zip file)`_).

Note that you have to *configure* sumo after installing it, see 
`The sumo configuration file`_.

Install from source (tar.gz or zip file)
++++++++++++++++++++++++++++++++++++++++

In this case download the package from 

 `sumo download page <https://sourceforge.net/projects/epics-sumo/files/?source=navbar>`_

unpack the tar.gz file with::

  tar -xzf <PACKAGENAME>

or unpack the zip file with::

  unzip <PACKAGENAME>

The sumo distribution contains the install script "setup.py". If you install
sumo from source you always invoke this script with some command line options. 

The following chapters are just *examples* how you could install sumo. For a
complete list of all possibilities see 
`Installing Python Modules <https://docs.python.org/2/install/index.html#install-index>`_.

Note that the python interpreter you use to start setup.py determines for which python version sumo is installed. 

In order to install for python 2.x use::

  python2 setup.py [options]

In order to install for python 3.x use::

  python3 setup.py [options]

Whenever ``python`` is mentioned in a command line in the following text remember
to use ``python2`` or ``python3`` instead.

Install as root to default directories
::::::::::::::::::::::::::::::::::::::

This method will install sumo on your systems default python library and
binary directories.

Advantages:

- You don't have to modify environment variables in order to use sumo.
- All users on your machine can easily use sumo.

Disadvantages:

- You must have root or administrator permissions to install sumo.
- Files of sumo are mixed with other files from your system in the same
  directories making it harder to uninstall sumo.

For installing sumo this way, as user "root" enter::

  python setup.py install

Install to a separate directory
:::::::::::::::::::::::::::::::

In this case all files of sumo will be installed to a separate directory.

Advantages:

- All sumo files are below a directory you specify, making it easy to uninstall
  sumo.
- If you have write access that the directory, you don't need root or
  administrator permissions.

Disadvantages:

- Each user on your machine who wants to use sumo must have the correct
  settings of the environment variables PATH and PYTHONPATH.

For installing sumo this way, enter::

  python setup.py install --prefix <DIR>

where <DIR> is your install directory.

In order to use sumo, you have to change the environment variables PATH and
PYTHONPATH. Here is an example how you could do this::

  export PATH=<DIR>/bin:$PATH
  export PYTHONPATH=<DIR>/lib/python<X.Y>/site-packages:$PYTHONPATH

where <DIR> is your install directory and <X.Y> is your python version number.
You get your python version with this command::

  python -c 'from sys import *;stdout.write("%s.%s\n"%version_info[:2])'

You may want to add the environment settings ("export...") to your shell setup,
e.g. $HOME/.bashrc or, if your are the system administrator, to the global
shell setup.

Install in your home
::::::::::::::::::::

In this case all files of sumo are installed in a directory in your home called
"sumo".

Advantages:

- All sumo files are below $HOME/sumo, making it easy to uninstall sumo.
- You don't need root or administrator permissions.

Disadvantages:

- Only you can use this installation.
- You need the correct settings of environment variables PATH and
  PYTHONPATH.

For installing sumo this way, enter::

  python setup.py install --home $HOME/sumo

You must set your environment like this::

  export PATH=$HOME/sumo/bin:$PATH
  export PYTHONPATH=$HOME/sumo/lib/python:$PYTHONPATH

You may want to add these lines to your shell setup, e.g. $HOME/.bashrc.

The sumo configuration file
---------------------------

In order to use sumo on your system you should create a configuration file. The
default name for this file is "sumo.config". See :doc:`configuration-files` for
a complete description of configuration files, see 
:ref:`sumo.config examples <configuration-files-config-examples>` for examples
of configuration files.

