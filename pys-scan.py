#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

"""
===========
pys-scan.py
===========

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
import re

import pys_utils as utils

# version of the program:
my_version= "1.0"

IGNORE_NAMES= set(["TOP", "EPICS_BASE"])

# temporarily search modules in my local bii_scripts copy:
# @@@@@
sys.path.insert(0, "/home/pfeiffer/net/project/bii_scripts/lib/python")

import makefile_scan

makefile_scan_pre= {}

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

def name2path_from_deps(deps):
    """calculate name2path dict from dependency dict.
    """
    name2path= {}
    for dependends in deps.values():
        for name, dep_path in dependends.items():
            utils.dict_of_sets_add(name2path, name, dep_path)
    return utils.dict_sets_to_lists(name2path)

def path2name_from_deps(deps):
    """calculate path2name dict from dependency dict.
    """
    path2name= {}
    for dependends in deps.values():
        for name, dep_path in dependends.items():
            utils.dict_of_sets_add(path2name, dep_path, name)
    return utils.dict_sets_to_lists(path2name)

def groups_from_deps(deps):
    """try to group directories.
    """
    def _add(dict_, p):
        """add a path."""
        (head,tail)= os.path.split(p)
        dict_.setdefault(head, set()).add(tail)
    groups= {}
    for path, dependencies in deps.items():
        _add(groups, path)
        for deppath in dependencies.values():
            _add(groups, deppath)
    new= {}
    for k, v in groups.items():
        name= os.path.basename(k).upper()
        new[name]= { "path": k,
                     "versions": sorted(v)
                   }
    return new


def filter_exclude_paths(deps, regexp):
    """remove all paths that match regexp.
    """
    rx= re.compile(regexp)
    new= {}
    for path, dependency_dict in deps.items():
        if rx.search(path):
            continue
        new[path]= dependency_dict
    return new

def filter_exclude_deps(deps, regexp):
    """remove all paths whose dependencies match regexp.
    """
    rx= re.compile(regexp)
    new= {}
    for path, dependency_dict in deps.items():
        matched= False
        for _, dep in dependency_dict.items():
            if rx.search(dep):
                matched= True
                break
        if not matched:
            new[path]= dependency_dict
    return new

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
    results= None
    if options.dir:
        results= get_dependencies(options)
    elif options.info_file:
        results= utils.json_loadfile(options.info_file)

    if not results:
        required=["--dir","--info-file"]
        sys.exit("error, one of these options must be provided: %s" % \
                 (" ".join(required)))
    if options.exclude_paths:
        results= filter_exclude_paths(results, options.exclude_paths)
    if options.exclude_deps:
        results= filter_exclude_deps(results, options.exclude_deps)
    if options.groups:
        utils.json_dump( groups_from_deps(results))
        return
    if options.name2paths:
        utils.json_dump( name2path_from_deps(results))
        return
    if options.path2names:
        utils.json_dump( path2name_from_deps(results))
        return
    utils.json_dump(results)

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
    parser.add_option("-i","--info-file",
                      action="store", 
                      type="string",  
                      help="read information from INFOFILE. This is a "+ \
                           "file generated by this script in a prevous run.",
                      metavar="INFOFILE"  
                      )
    parser.add_option("--groups",
                      action="store_true", 
                      help="try to group directories by their name",
                      )
    parser.add_option("--name2paths",
                      action="store_true", 
                      help="return a map mapping names to paths",
                      )
    parser.add_option("--path2names",
                      action="store_true", 
                      help="return a map mapping paths to names",
                      )
    parser.add_option("--exclude-paths",
                      action="store", 
                      type="string",  
                      help="exclude all paths that match REGEXP "+ \
                           "from dependencies",
                      metavar="REGEXP"  
                      )
    parser.add_option("--exclude-deps",
                      action="store", 
                      type="string",  
                      help="exclude all paths whose dependencies "+ \
                           "match REGEXP",
                      metavar="REGEXP"  
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

