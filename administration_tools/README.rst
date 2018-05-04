sumo administration scripts
===========================

How to create a new release
---------------------------

Create a new version
++++++++++++++++++++

Show the current version with this command::

  ./show-version.sh

Make up a new version VERSION and create it with::

  ./new-version.sh <VERSION>

Rebuild documentation
+++++++++++++++++++++

Enter this command::

  ./doc-rebuild.sh

Create tar.gz distribution files
++++++++++++++++++++++++++++++++

Enter these commands::

  ./cleanup-distdirs.sh
  ./mk-dist.sh

Create docker images
++++++++++++++++++++

Check if the docker images for sumo exist::

  docker images | grep sumo

If you see nothing, create the images with::

  ./docker-build-all.sh

Now create all sumo packages with::

  ./docker-run-all.sh

Upload files to sourceforge
+++++++++++++++++++++++++++

Upload the documentation with::

  ./sourceforge-upload-html.sh

Upload the distribution files with::

  ./sourceforge-upload-distfiles.sh

Upload files to bitbucket
+++++++++++++++++++++++++

Upload the documentation with::

  ./bitbucket-upload-html.sh

Upload the distribution files with::

  ./bitbucket-prepare-distfiles.sh

and follow the instructions printed on the console. Note
that you have to be logged in at Bitbucket before you can 
do this. You do the actual uploading in a web browser.

Prepare the local repository
++++++++++++++++++++++++++++

Use these commands to change mq patches to regular mercurial patches::

  hg qcommit -m backup
  hg qfinish -a

Give a tag::

  hg tag <VERSION>

upload the repository to sourceforge
++++++++++++++++++++++++++++++++++++

Push all patches to the central sourceforge repository::

  ./sourceforge-push.sh

upload the repository to bitbucket
++++++++++++++++++++++++++++++++++

Enter this command::

  ./bitbucket-push.sh

Upload to pypi
++++++++++++++

Note: ~/.pypirc must have this content (password omitted here)::

  [distutils]
  index-servers=
      pypi
      testpypi
  
  [testpypi]
  repository = https://test.pypi.org/legacy/
  username = Goetz.Pfeiffer
  password = ***
  
  [pypi]
  username = Goetz.Pfeiffer
  password = ***

Since you cannot undo an upload of a specific version, first test with the
pypi test site.

pypi test site
::::::::::::::

Run::

  ./pypi-test-upload.sh

Now test with these commands for python 2::

  virtualenv tmp
  cd tmp
  source bin/activate
  pip install EPICS-sumo -i https://testpypi.python.org/pypi
  sumo -h
  <ctrl-d>

If everything worked, remove the test directory with::

  rm -rf tmp

Now test with these commands for python 3::

  virtualenv-3 tmp
  cd tmp
  source bin/activate
  pip install EPICS-sumo -i https://testpypi.python.org/pypi
  sumo -h
  <ctrl-d>

If everything worked, remove the test directory with::

  rm -rf tmp

pypi site
:::::::::

Upload to pypi with::

  ./pypi-upload.sh

Explanation of scripts
----------------------

Sourceforge administration
++++++++++++++++++++++++++

sourceforge-shell.sh
  Open an interactive shell at sourceforge.

sourceforge-upload-distfiles.sh
  Upload files from "dist" directory to sourceforge.

sourceforge-upload-html.sh
  Upload html documentation to sourceforge.

Bitbucket administration
++++++++++++++++++++++++

bitbucket-push.sh
  Push patches to mercurial repository at Bitbucket.

bitbucket-transfer-html.sh
  Transfer documentation to my Bitbucket documentation repository.

bitbucket-upload-distfiles.sh
  Prepare upload of distfiles to Bitbucket requires still some actions in
  firefox.

bitbucket-web-checkout.sh
  Checkout bitbucket website repo.

Version handling
++++++++++++++++

check-version.sh
  Check if version numbers are consistent.

show-version.sh
  Show version numbers in all scripts and modules.

new-version.sh
  Create a new version (see "Steps to create a new release" in this file).

Documentation
+++++++++++++

doc-rebuild.sh
  Rebuild the html documentation

Create distribution files
+++++++++++++++++++++++++

mk-dist.sh
  Create distribution (*.tar.gz) files

cleanup-distdirs.sh
  Clean the distribution directory

mk-rpm.sh
  Create an rpm file (works only on a fedora system)

mk-deb.sh
  Create a debian file, should be used on a debian system or a debian docker
  container.

pypi support
++++++++++++

pypi-upload.sh
  Upload a new version to pypi.

pypi-test-upload.sh
  Upload a new version to the pypi test server.

Docker support
++++++++++++++

docker          
  The directory with the docker files

docker-build.sh
  Build docker debian containers needed for mk-xxx.sh scripts run this as
  docker-build.sh <system-name> with system-name one of: debian-7 debian-8
  fedora-21 fedora-22

docker-build-all.sh 
  Build docker containers for all supported linux systems.

docker-run.sh
  Run a docker container run this as docker-run.sh <system-name> with
  system-name one of: debian-7 debian-8 fedora-21 fedora-22

docker-run-all.sh
  Build packages for all supported linux systems.

mk-deb.sh
  Create debian packages, called from within the debian docker container.

mk-rpm.sh
  Create rpm packages, called from within the fedora docker container.
