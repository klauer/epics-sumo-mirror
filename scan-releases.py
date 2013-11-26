#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

"""
================
scan-releases.py
================

Introduction
------------

This programs scans an EPICS support directory tree as it is used at BESSY and
returns the found dependencies in JSON format.

How the program operates
------------------------

The program calls the "make" program in order to evaluate each "RELEASE" file
found in the "configure" directories of the support directories. In these files
there is a definition of a make macro for each dependency like shown here::

  SUPPORT=/opt/Epics/R3.14.8/support
  MISC=$(SUPPORT)/misc/2-4
  ALARM=$(SUPPORT)/alarm/3-1
  SOFT=$(SUPPORT)/soft/2-2

"make" resolves all macros, so "$(SUPPORT)" is replaced by the value of macro
SUPPORT. It returns adds all macros to the set of pre-defined environment
variables and returns the complete set of variables.

This script has a list of all variables that are defined in make if it is
called without any given file. This set is subtracted from the returned set
leaving all macros that were defined in the RELEASE file. The script returns a
list of macros as a map for each support path that was found.

Example output
--------------

For the example shown above, which was taken from the file
"/opt/Epics/R3.14.8/support/mcan/2-3/configure/RELEASE" the script would return
this::

  {
      "/opt/Epics/R3.14.8/support/mcan/2-3": {
          "ALARM": "/opt/Epics/R3.14.8/support/alarm/3-1",
          "MISC": "/opt/Epics/R3.14.8/support/misc/2-4",
          "SOFT": "/opt/Epics/R3.14.8/support/soft/2-2"
      },
  }
"""

# pylint: disable=C0322,C0103

from optparse import OptionParser
import sys
import os.path
import os
import subprocess

import pysupport_utils as utils

# version of the program:
my_version= "1.0"

IGNORE_NAMES= set(["TOP", "EPICS_BASE"])

# temporarily search modules in my local bii_scripts copy:
# @@@@@
sys.path.insert(0, "/home/pfeiffer/net/project/bii_scripts/lib/python")

import makefile_scan

makefile_scan_pre= {}

# -----------------------------------------------
# small utilities
# -----------------------------------------------

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
# RELEASE file scanning
# -----------------------------------------------

def scan_release_file(filename, external_definitions= None, 
                      verbose= False, dry_run= False):
    """scan a release file.
    """
    data= makefile_scan.scan(filename, 
                             external_definitions,
                             makefile_scan_pre,
                             verbose, dry_run)
    dependencies= {}
    for (k,v) in data.items():
        if not os.path.exists(v):
            continue
        if not "support" in v:
            continue
        if v.endswith("support"):
            continue
        if k in IGNORE_NAMES: # names to ignore
            continue
        v= v.replace("//","/") # replace double-slashes
        dependencies[k]= v
    return dependencies

def scan_support_release(support_path, 
                         verbose= False, dry_run= False):
    """scan the RELEASE file of a support.
    """
    external_definitions= { "TOP": support_path }
    return scan_release_file(os.path.join(support_path,"configure","RELEASE"),
                             external_definitions,
                             verbose= verbose, dry_run= dry_run)

def dependency_data(support_tree, progress= False, 
                    verbose= False, dry_run= False):
    """scan a whole file-tree.
    """
    def slicer(l, val):
        """changes a list to a single element list.
        
        This function *directly* modifies the list instead of creating a new
        one. This is needed for the os.walk function.
        """
        try:
            i= l.index(val)
        except ValueError, _:
            return l
        l[i+1:]= []
        l[0:i]= []
        return l
    dict_= {}
    cnt_max= 50
    cnt= 0
    if progress:
        utils.show_progress(cnt, cnt_max, "directories searched for RELEASE")
    for (dirpath, dirnames, filenames) in os.walk(support_tree, topdown= True):
        if progress:
            cnt= utils.show_progress(cnt, cnt_max)
        slicer(dirnames, "configure")
        if os.path.basename(dirpath)=="configure":
            if "RELEASE" in filenames:
                # get the path of the versioned support:
                versioned_path= os.path.dirname(dirpath)
                data= scan_support_release(versioned_path,
                                           verbose= verbose, dry_run= dry_run)
                dict_[versioned_path]= data
    if progress:
        sys.stderr.write("\n")
    return dict_


# -----------------------------------------------
# main
# -----------------------------------------------

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def get_dependencies(options):
    """get the dependencies.
    """
    if not options.dir:
        sys.exit("--dir is mandatory")
    deps= \
       dependency_data(options.dir,
                       options.progress,
                       options.verbose,
                       options.dry_run
                      )
    return deps


def process(options):
    """do all the work.
    """
    if options.dir:
        results= get_dependencies(options)
        utils.json_dump(results)
    else:
        sys.exit("--dir is mandatory")

def print_doc():
    """print a short summary of the scripts function."""
    print __doc__

def print_summary():
    """print a short summary of the scripts function."""
    print "%-20s: a tool for scanning support EPICS trees \n" % \
          script_shortname()

def _test():
    """does a self-test of some functions defined here."""
    print "performing self test..."
    import doctest
    doctest.testmod()
    print "done!"

def main():
    """The main function.

    parse the command-line options and perform the command
    """
    # command-line options and command-line help:
    usage = "usage: %prog [options] {files}"

    parser = OptionParser(usage=usage,
                          version="%%prog %s" % my_version,
                          description="This program scans EPICS support "+\
                              "trees and prints the found dependencies "+\
                              "to the screen",
                         )

    parser.add_option("--summary",  
                      action="store_true", 
                      help="print a summary of the function of the program",
                      )
    parser.add_option("--doc",  
                      action="store_true", 
                      help="print a longer description of the program",
                      )
    parser.add_option("--test",  
                      action="store_true",
                      help="perform simple self-test", 
                      )
    parser.add_option("-d", "--dir",
                      action="store", 
                      type="string",  
                      help="parse all RELEASE files in directory DIR",
                      metavar="DIR"  
                      )
    parser.add_option("-p", "--progress", 
                      action="store_true", 
                      help="show progress on stderr",
                      )
    parser.add_option("-v", "--verbose",   
                      action="store_true", 
                      help="show command calls ",
                      )
    parser.add_option("-n", "--dry-run",   
                      action="store_true", 
                      help="just show what the program would do",
                      )

    x= sys.argv
    (options, args) = parser.parse_args()
    # options: the options-object
    # args: list of left-over args

    if options.summary:
        print_summary()
        sys.exit(0)

    if options.doc:
        print_doc()
        sys.exit(0)

    if options.test:
        _test()
        sys.exit(0)

    # we could pass "args" as an additional parameter to process here if it
    # would be needed to process remaining command line arguments.
    process(options)
    sys.exit(0)

if __name__ == "__main__":
    main()

