Release 4.0.1
-------------

Date: 2020-03-10

(Changes with respect to relase 4.0)

Bugfixes
++++++++

- With python 3.2.3, errors while checking out modules were not recognized.
- error messages from checking out darcs repos are now reproducible

Release 4.0.2
-------------

Date: 2020-06-02

Internal changes
++++++++++++++++

- Platforms where tests succeeded are now documented in test/tests.log

Bugfixes
++++++++

- Do not use "git -C" since older versions of git don't support this

Release 4.1
-----------

Date: 2020-08-30

Internal changes
++++++++++++++++

- All docker scripts were moved to administration_tools/docker
- Various improvements in dockerscripts, can now use podman instead of docker
- Package support for fedora-30 was removed, fedora-32 was added instead
- removed pylint warnings in various files
- add a test that checks what happens if we try to create a build that 
  already exists
- Support for creating code coverage statistics of the tests was added
- some comments in the code regarding "sumo build try" were added.
- optimized "git clone", if a tag or branch is given, it is now provided 
  with option "-b" to git

Bugfixes
++++++++

- Small bugfix in the documentation
- fixed a misleadung error message when locking file DEPS.DB fails
- option "--dry-run" sometimes raised an exception when sumo should have
  created a file. With "--dry-run" sumo should only show what it would have 
  done, but not make any changes on files.
- give a proper error message when "sumo build try ... --exclude-states"
  gets an invalid regular expression, added testcode for this
- Option "--dry-run" is now better supported. All functions that do changes
  to files shouldn't change anything when "--dry-run" is used and just
  print to the console what they would have done.

Documentation
+++++++++++++

- "configuration file" was added to the glossary
- small improvements
- an example how to re-create a build with the help of "sumo build showmodules"
  was added

New/Changed functions
+++++++++++++++++++++

- The help of command line options is now sorted alphabetically
- added "sumo build showmodules", this list all modules used in a build in 
  the form MODULE:VERSION which is compatible with the format sumo option
  "-m" expects. An example how to use this is in the documentation.
- added "sumo build showdependencies", this shows all builds the given 
  build depends on
- added "sumo build showdependents", this shows all builds the depend
  on the given build
- "sumo build new" now first checks if a matching build exists. If it does,
  the command aborts with an error message. If option --no-err-build-exists
  is given, the command prints a warning and stops without error code.
- many "sumo build" commands that print information about builds can now sort
  the builds by their dependency relations. With
  --sort-build-dependencies-first, dependencies of a build always come before
  the build.  With --sort-build-dependencies-last, dependencies of a build
  always come after the build. 
- commands that list or show builds now ignore builds that do not have the 
  state "stable" or "testing". You must use option "--all-builds" to see
  the other builds, too.
- the template for "sumo config new ... github" was extended and improved,
  some modules were updated and AREADETECTOR was added.

Compatibility
+++++++++++++

- Command "sumo build list" now only shows builds with the state "stable" or
  "testing". Before sumo 4.1 it used to show *all* builds. In order for the
  command to do the same as in older versions of sumo, add option
  "--all-builds" like in "sumo build list --all-builds".
