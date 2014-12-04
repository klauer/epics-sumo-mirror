Installing Sumo
===============

Parts of sumo
-------------

Sumo consists of some scripts, some python modules, some documentation and
configuration files. 

The sumo distribution does not contain the configuration files since you have
to adapt them to your development host. Examples of configuration files are
shown further below.

The install script
------------------

The sumo distribution contains the install script "setup.py". You always
install sumo by invoking this script with some command line options. 

The following chapters are just *examples* how you could install sumo. For a
complete list of all possibilities see 
`Installing Python Modules <https://docs.python.org/2/install/index.html#install-index>`_.

Install examples
++++++++++++++++

Here we show some possible ways on how to start the install script.

Install as root to default directories
::::::::::::::::::::::::::::::::::::::

This method will install sumo to your systems default python library and binary
directories.

Advantages:

- You don't have to modify environment variables in order to use sumo.
- All users on your machine can easily use sumo.

Disadvantages:

- You have to have root or administrator rights to install sumo.
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
- If you have write access to the directory, you don't need to have root or
  administrator rights.

Disadvantages:

- Each user on your machine who wants to use sumo has to have the proper
  setting of the environment variables PATH and PYTHONPATH.

For installing sumo this way, enter::

  python setup.py install --prefix <DIR>

where <DIR> is your install directory.

In order to use sumo, you have to change the environment variables PATH and PYTHONPATH. Here is an example how you could do this::

  export PATH=<DIR>/bin:$PATH
  export PYTHONPATH=<DIR>/lib/python<X.Y>/site-packages:$PYTHONPATH

where <DIR> is your install directory and <X.Y> is your python version number. You can get your python version with this command::

  python -c 'import sys;print "%s.%s"%sys.version_info[:2]'

You may want to add the environment settings ("export...") to your shell setup,
e.g. $HOME/.bashrc or, if your are the system administrator, to the global
shell setup.

Install in your home
::::::::::::::::::::

In this case all files of sumo are installed in a directory in your home called
"sumo".

Advantages:

- All sumo files are below $HOME/sumo, making it easy to uninstall sumo.
- You don't need to have root or administrator rights.

Disadvantages:

- Only you can use this install.
- You have to have the proper setting of the environment variables PATH and
  PYTHONPATH.

For installing sumo this way, enter::

  python setup.py install --home $HOME/sumo

You have to set your environment like this::

  export PATH=$HOME/sumo/bin:$PATH
  export PYTHONPATH=$HOME/lib/python:$PYTHONPATH

You may want to add these lines to your shell setup, e.g. $HOME/.bashrc.

The sumo configuration file
---------------------------

In order to use sumo on your system you should create a configuration file. See
:doc:`configuration-files` how to do this. 

For examples on configuration files see 
:ref:`sumo.config examples <configuration-files-config-examples>`.

