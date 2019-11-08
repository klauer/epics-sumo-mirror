Sumo Tests
==========

Preface
-------

All tests in this directory are started by invoking make. 

Prepatations for the tests
--------------------------

You have to run the following commands before starting the tests::

  ../administration_tools/mk-data.sh 
  ../administration_tools/mk-sumo-doc.sh

The python version
------------------

Wether tests are performed for the python2 or python3 version is decided by the
setting of environment variable PYVER.

In order to test python2, set PYVER like this::

  export PYVER=2

In order to test python3, set PYVER like this::

  export PYVER=3

Note that on order to test python2 *and* python3 you have to run "make clean"
between the tests. So you should test both python versions like this::

  PYVER=2 make all -sj
  PYVER=2 make clean
  PYVER=3 make all -sj

Types of tests
--------------

Module tests
++++++++++++

The python modules of this project contain doctests (see documentation of
"python doctest") in the docstrings of functions.

These tests are performed by executing python modules with the python
intepreter. The commands and expected output are specified in the docstrings.

Script selftests
++++++++++++++++

If scripts of this project are invoked with option "--test" tests are run
according to the doctest tests specified in docstrings.

Shell tests
+++++++++++

These are the most generic form of tests. Shell scripts test a certain function
of the program and print output to the console. This output is directed to a
\*.out file. That file is compared with a \*.ok file, if both are identical,
the test is assumed to have succeeded.

Version control system tests
++++++++++++++++++++++++++++

In order to test support of varous version control systems, software
repositories are created before the tests are run. Since it takes a rather long
time to create these, "make clean" does not remove the created software
repositories. These are onle removed when "make distclean" is invoked.

Make
----

Parallel make
+++++++++++++

You can run make with option "-j", on multi core CPUs the tests run much faster
with this. With option "-s" you suppress the printing of the executed commands
which makes the output more readable.

Test order and dependencies
+++++++++++++++++++++++++++

Some tests depend on the results of other tests. These dependencies are
specified in the makefile.

Errors
------

If the \*.ok and \*.out file of a test differ, the difference is printed on the
console and the tests stop. Here is an example output of the command 
``make -sj``::

  -> Test sumo build try
  159a160,175
  > MISC_DEBUGMSG/R3-0+AUTO-001/sumo-all:
  > 	cd $(@D) && rm -f sumo-all sumo-config sumo-clean sumo-distclean
  > 	touch $@
  > 
  > MISC_DEBUGMSG/R3-0+AUTO-001/sumo-clean:
  > 	cd $(@D) && rm -f sumo-all sumo-config sumo-clean sumo-distclean
  > 	touch $@
  > 
  > MISC_DEBUGMSG/R3-0+AUTO-001/sumo-config:
  > 	cd $(@D) && rm -f sumo-all sumo-config sumo-clean sumo-distclean
  > 	touch $@
  > 
  > MISC_DEBUGMSG/R3-0+AUTO-001/sumo-distclean:
  > 	cd $(@D) && rm -f sumo-all sumo-config sumo-clean sumo-distclean
  > 	touch $@
  > 
  make: *** [Makefile:209: sumo-build-new-make-recipes.tst] Error 1
  make: *** Waiting for unfinished jobs....

Note that due to the parallel execution of the test, the line at the top *does
not* show which test failed. You can see this at the bottom line. \*.tst is a
file that is generated when the test succeeds. You may compare the output and
expected output in this example with this command::

  diff sumo-build-new-make-recipes.o*

In order to re-run this test alone enter (note that PYVER must be set)::

  make sumo-build-new-make-recipes.clean
  make sumo-build-new-make-recipes.tst

Run a test separately
---------------------

Each test has a name. All names are listed in file TESTS. 

When a test succeeds a file TESTNAME.tst is created. 

You remove all files created by a test with the command::

  make TESTNAME.clean

You run a test separately with the command::

  make TESTNAME.tst

If the test fails, you should compare the TESTNAME.ok and TESTNAME.out file.
This command shows the differences as textual diff::

  diff TESTNAME.o*

Online help
-----------

Invoking::

  make help

shows a short online help.

