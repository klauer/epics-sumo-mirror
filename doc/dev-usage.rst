Develop support modules with sumo
=================================

sumo makes developing support modules easier. In this example we want to apply
changes in an existing support module, here "ALARM:R3-8". 

For our development we want to create a "sandbox" directory where we change and
compile the new support module. There are two ways to do this:

standalone:
  We use a local copy of the dependency database and build all support modules
  in a local directory.

local:
  We use a local copy of the dependency database, build all support modules in
  a local directory but use existing compiled support modules from a global
  build directory.

For both cases sumo create a configuration file "sumo.config" that contains all
needed settings and create the sandbox directory if it does not yet exist.

In the following example we create a sandbox in "local" mode.

Create the sandbox
------------------

Decide what the name of the sandbox should be, here we use "sandbox" and enter
this command::

  sumo config local sandbox

Create a "HEAD" version of a module
-----------------------------------

We now create a new entry in our local dependency database for the test version
of module "ALARM"::

  sumo db cloneversion ALARM R3-8 HEAD darcs .

Answer 'y' when the program asks if the changes are correct.

Build the module for the first time
-----------------------------------

We first have to see which other modules are needed by "ALARM"::

  sumo build try ALARM:HEAD --detail 1

This produces the following output::

  Possible versions for unspecified/missing modules:
  
  BASE                R3-14-10-0-1 R3-14-12-2-1 R3-14-12-2-1-aragon2
                      R3-14-12-2-1-aragon3 R3-14-12-2-1-aragon4
                      R3-14-12-2-1-aragon5 R3-14-12-2-1-aragon6
                      R3-14-12-2-4 R3-14-12-2-5 R3-14-12-2-6
                      R3-14-12-2-7 R3-14-8-2-0 R3-14-8-2-1
  BSPDEP_TIMER        R4-0 R5-0 R5-1 R6-2
  MISC_DBC            R3-0
  
  Not all dependencies were included in module specifications, these modules
  have to be added:
      BASE
      BSPDEP_TIMER
      MISC_DBC
  
  Command 'new' would create build with tag 'local-BL-001'
  
  Your module specifications are still incomplete, command 'new' can not
  be used with these.

We specify the missing modules directly on the command line and create a new
build with the "HEAD" version of "ALARM"::

  sumo build new ALARM:HEAD BASE:R3-14-12-2-1-aragon6 BSPDEP_TIMER:R6-2 MISC_DBC:R3-0

We see the name of the new created build with::

  sumo build list | grep local-

Change and recompile
--------------------

We can now apply changes directly in directory::

  sandbox/build/ALARM/HEAD+local-BL-001

We recompile the module and it's dependencies with::

  sumo build remake local-BL-001

Test in an application
----------------------

In our application directory we first have to set up usage of the sumo sandbox::

  sumo config local sandbox

When asked "Directory 'sandbox' already exists, use it ?" answer "y".

In order to test our support change the definition of "ALARM" in file
"configure/MODULES" to::

  ALARM:HEAD

Then use the new support with::

  sumo build use

then create the application::

  make clean && make

You can now test the support in your application.
