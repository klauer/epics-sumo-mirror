sumo administration scripts
===========================

How to create a new release
---------------------------

Update RELEASES.rst
+++++++++++++++++++

Create a LOG file like this::

  hg log --style changelog -r $(./show-last-release.sh):tip > LOG

Now get the current version::

  ./show-version.sh

and make up a new version number.

Manually add new entries to RELEASES.rst like this::

  nvim -o LOG ../RELEASES.rst

Create a new entry at the end with today's date and the new VERSION number 
like in this example::

  Release 4.1.1
  -------------
  
  Date: 2020-09-11
  
Create a new version
++++++++++++++++++++

Set up a new version like this::

  ./new-version.sh $(./show-last-release.sh)

Setup data directories
++++++++++++++++++++++

Enter this command::

  ./mk-data.sh

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

Change directory do docker::

  cd docker

Create docker images, if they do not already exist::

  ./docker-build-all.sh

Now create all sumo packages with::

  ./docker-run-all.sh

Go back to parent directory::

  cd ..

Upload files to sourceforge
+++++++++++++++++++++++++++

Upload the documentation with::

  ./sourceforge-upload-html.sh

Upload the distribution files with::

  ./sourceforge-upload-distfiles.sh

Prepare the local repository
++++++++++++++++++++++++++++

Use these commands to change mq patches to regular mercurial patches::

  hg qcommit -m backup
  hg qfinish -a

Give a tag::

  hg tag $(./show-last-release.sh)

upload the repository to sourceforge
++++++++++++++++++++++++++++++++++++

Push all patches to the central sourceforge repository::

  ./sourceforge-push.sh

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

Now test with these commands::

  python3 -m venv tmp
  cd tmp
  bash
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

Third party tools needed for documentation generation
-----------------------------------------------------

You need the following tools:

sphinx
++++++

Homepage: https://www.sphinx-doc.org/en/master/

Package name on fedora systems: python3-sphinx

Installation: Use your package manager

ReadTheDocs
+++++++++++

Homepage: https://sphinx-rtd-theme.readthedocs.io/en/stable/

Installation: Install with pip::

  pip install sphinx_rtd_theme

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

mk-sumo-doc.sh
  Create python modules with sumo online documentation.

doc-rebuild.sh
  Rebuild the html documentation

Create distribution files
+++++++++++++++++++++++++

mk-dist.sh
  Create distribution (\*.tar.gz) files

cleanup-distdirs.sh
  Clean the distribution directory

mk-rpm.sh
  Create an rpm file (works only on a fedora system)

mk-deb.sh
  Create a debian file, should be used on a debian system or a debian docker
  container.

Cleanup working copy 
++++++++++++++++++++

distclean.sh
  Removes all generated files, only files under version control are left.

pypi support
++++++++++++

pypi-upload.sh
  Upload a new version to pypi.

pypi-test-upload.sh
  Upload a new version to the pypi test server.

Docker support
++++++++++++++

All files for the docker support are in sub-directory "docker".

docker/dockerfiles
  The directory with the docker files

docker/docker-build.sh
  Build docker debian containers needed for mk-xxx.sh scripts run this as
  docker-build.sh DOCKERFILE. All possible DOCKERFILE names are shown with
  option "-h".

docker/docker-build-all.sh 
  Build docker containers for all supported linux systems.

docker/docker-run.sh
  Run a docker container run this as docker-run.sh DOCKERFILE, run this as
  docker-build.sh DOCKERFILE. All possible DOCKERFILE names are shown with
  option "-h".

docker/docker-run-all.sh
  Build packages for all supported linux systems.

docker/mk-deb.sh
  Create debian packages, called from within the debian docker container.

docker/mk-rpm.sh
  Create rpm packages, called from within the fedora docker container.

