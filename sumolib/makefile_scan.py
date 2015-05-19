"""
=============
makefile_scan
=============

Scan definitions in a makefile or a list of makefiles. This module
actually calls "make" in order to examine the files and returns the
values of all variables or makefile macros as a dictionary.

The main function in this module is "scan". "scan" is called like this::

  data= scan(filenames, verbose, dry_run)

Parameters are:

filenames
  A single filename or a list of filenames

verbose
  A boolean, if True print all system command calls to the console.

dry_run
  A boolean, if True just print the system command calls but do not
  execute them.

"""

import os.path
import re
import sys

import sumolib.system

# pylint: disable=C0322,C0103

__version__="2.8.2" #VERSION#

assert __version__==sumolib.system.__version__

# -----------------------------------------------
# makefile scanning
# -----------------------------------------------

rx_def= re.compile(r'^(\w+)=(.*)$')

def _scan(filenames, external_definitions= None,
          warnings= True,
          verbose= False, dry_run= False):
    """scan makefile-like definitions.
    """
    # pylint: disable=R0914
    #                          Too many local variables
    for f in filenames:
        if not os.path.exists(f):
            raise IOError("file \"%s\" does not exist" % f)
    if filenames:
        include_cmd= "include " + (" ".join(filenames))
    else:
        include_cmd= ""
    extra= ""
    if external_definitions:
        l= []
        for (k,v) in external_definitions.items():
            l.append("%s=\"%s\"" % (k,v))
        l.append("")
        extra= " ".join(l)
    cmd=("/bin/echo -e \"%s\\n" +\
         ".EXPORT_ALL_VARIABLES:\\n" +\
	 "scan_makefile_pe:\\n" +\
	 "\\t@printenv\\n\" | %s " +\
	 "make -s -f - scan_makefile_pe") % (include_cmd,extra)
    data= {}
    (reply,_)= sumolib.system.system(cmd, True, False, verbose, dry_run)
    if dry_run:
        return data
    for line in reply.splitlines():
        m= rx_def.match(line)
        if m is None:
            if warnings:
                sys.stderr.write("\nmakefile_scan.py: warning:\n"
                                 "\tline not parsable in %s\n"
                                 "\t'%s'\n" % (" ".join(filenames),line))
            continue
        data[m.group(1)]= m.group(2)
    return data

def scan(filenames, external_definitions= None, pre= None,
         warnings= True,
         verbose= False, dry_run= False):
    """scan makefile-like definitions.

    This takes a makefile name or a list of makefile names and returns a
    dictionary with all definitions made in these files. All definitions
    are resolved meaning that all variables that are used in the values
    of definitions are replaces with their values.

    filenames
        a single filename (string) or a list of filenames (list of strings)

    external_definitions
        A dict with variable settings that are pre-defined.

    pre
        None or a dict. For consecutive calls of this function providing an
        initially empty dictionary here speeds up calls by a factor of 2.

    warnings
        print a warning when a line cannot be parsed

    verbose
        if True, print command calls to the console

    dry_run
        if True, only print command calls to the console, do not return
        anything.

    """
    # pylint: disable=R0913
    #                          Too many arguments
    if isinstance(filenames, str):
        filenames= [filenames]
    if pre is None:
        pre= _scan([], external_definitions, warnings, verbose, dry_run)
    else:
        if not pre: # empty dict
            pre.update(_scan([], external_definitions, warnings,
                             verbose, dry_run))
    post= _scan(filenames, external_definitions, warnings, verbose, dry_run)
    new= {}
    for (k,v) in post.items():
        if pre.has_key(k):
            if pre[k]==post[k]:
                continue
        new[k]= v
    return new


