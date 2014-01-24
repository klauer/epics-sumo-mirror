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

import subprocess
import os.path
import re
import sys

# pylint: disable=C0322,C0103

# -----------------------------------------------
# basic system utilities
# -----------------------------------------------

def _system(cmd, catch_stdout, verbose, dry_run):
    """execute a command.

    execute a command and return the programs output
    may raise:
    IOError(errcode,stderr)
    OSError(errno,strerr)
    ValueError
    """
    if dry_run or verbose:
        print ">", cmd
        if dry_run:
            return None
    if catch_stdout:
        stdout_par=subprocess.PIPE
    else:
        stdout_par=None

    p= subprocess.Popen(cmd, shell=True,
                        stdout=stdout_par, stderr=subprocess.PIPE,
                        close_fds=True)
    (child_stdout, child_stderr) = p.communicate()
    # pylint: disable= E1101
    if p.returncode!=0:
        raise IOError(p.returncode,
                      "cmd \"%s\", errmsg \"%s\"" % (cmd,child_stderr))
    # pylint: enable= E1101
    return(child_stdout)

# -----------------------------------------------
# makefile scanning
# -----------------------------------------------

rx_def= re.compile(r'^(\w+)=(.*)$')

def _scan(filenames, external_definitions= None, 
          verbose= False, dry_run= False):
    """scan makefile-like definitions.
    """
    for f in filenames:
        if not os.path.exists(f):
            raise IOError, "file \"%s\" does not exist" % f
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
    cmd=("echo -e \"%s\\n" +\
         ".EXPORT_ALL_VARIABLES:\\n" +\
	 "scan_makefile_pe:\\n" +\
	 "\\t@printenv\\n\" | %s " +\
	 "make -s -e -f - scan_makefile_pe") % (include_cmd,extra)
    data= {}
    reply= _system(cmd, True, verbose, dry_run)
    if dry_run:
        return data
    for line in reply.splitlines():
        m= rx_def.match(line)
        if m is None:
            sys.stderr.write(("makefile_scan.py: line not "+ \
                              "parsable:\"%s\"\n") % line)
            continue
        data[m.group(1)]= m.group(2)
    return data

def scan(filenames, external_definitions= None, pre= None,
         verbose= False, dry_run= False):
    """scan makefile-like definitions.

    This takes a makefile name or a list of makefile names and returns a
    dictionary with all definitions made in these files. All definitions
    are resolved meaning that all variables that are used in the values
    of definitions are replaces with their values.

    parameters:
      filenames  - a single filename (string) or a list of filenames
                   (list of strings)
      external_definitions -
                   A dict with variable settings that are pre-defined.
      pre        - None or a dict. For consecutive calls of this function
                   providing an initially empty dictionary here speeds up calls
                   by a factor of 2.
      verbose    - if True, print command calls to the console
      dry_run    - if True, only print command calls to the console, do
                   not return anything.
    """
    if isinstance(filenames, str):
        filenames= [filenames]
    if pre is None:
        pre= _scan([], external_definitions, verbose, dry_run)
    else:
        if not pre: # empty dict
            pre.update(_scan([], external_definitions, verbose, dry_run))
    post= _scan(filenames, external_definitions, verbose, dry_run)
    new= {}
    for (k,v) in post.items():
        if pre.has_key(k):
            if pre[k]==post[k]:
                continue
        new[k]= v
    return new


