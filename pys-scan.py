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

KNOWN_COMMANDS=set(("deps", "name2paths", "path2names", "groups", "repos"))

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

def groups_from_deps(deps, basedir):
    """try to group directories.
    """
    def _add(dict_, p):
        """add a path."""
        (head,tail)= os.path.split(p)
        dict_.setdefault(head, set()).add(tail)
    def gen_name(name, basedir):
        """generate a module name."""
        if name.startswith(basedir):
            name= name.replace(basedir,"")
        if name[0]=="/":
            name= name[1:]
        name= name.replace("/","_")
        return name.upper()
    groups= {}
    for path, dependencies in deps.items():
        _add(groups, path)
        for deppath in dependencies.values():
            _add(groups, deppath)
    new= {}
    for k, v in groups.items():
        new[gen_name(k,basedir)]= { "path": k,
                                    "subdirs": sorted(v)
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
# repository scanning
# -----------------------------------------------

def all_paths_from_deps(deps):
    """get a collection of all paths from the dependency dict.
    """
    all_paths= set()
    for path, dependends in deps.items():
        all_paths.add(path)
        for dep_path in dependends.values():
            all_paths.add(dep_path)
    return all_paths

rx_darcs_repo= re.compile(r'^\s*Default Remote:\s*(.*)')

rx_darcs= re.compile(r'.*?(?:/darcs/epics|:darcs-repos/epics)/support(.*)')

def darcs_source_repo(directory, verbose, dry_run):
    """get the darcs source repository.

    This function calls "darcs show repo". If there is a "Default
    repository" it is returned. If this is not presents the function
    returns "Root repository" as it is returned from darcs.
    """
    def _canonify(darcspath):
        """convert the darcspath to a real dictionary.
        """
        return rx_darcs.sub(
                   r"/opt/repositories/controls/darcs/epics/support\1", 
                   darcspath)
    if not os.path.exists(os.path.join(directory,"_darcs")):
        return
    try:
        reply= utils.system("cd %s && darcs show repo" % directory, 
                             True, verbose, dry_run)
    except IOError, _:
        # probably no darcs repo found
        return
    default_repo= None
    for line in reply.splitlines():
        m= rx_darcs_repo.match(line)
        if m:
            r= _canonify(m.group(1).strip())
            if not os.path.exists(os.path.join(r,"_darcs")):
                continue
            default_repo= r
            continue
    url= directory
    if default_repo:
        url= default_repo
    #return url
    return _canonify(url)

def darcs_last_tag(directory, verbose, dry_run):
    """Returns the topmost darcs tag.
    """
    try:
        reply= utils.system("cd %s && darcs show tags" % directory, True, 
                             verbose, dry_run)
    except IOError, _:
        # probably no darcs repo found
        return
    if not reply:
        # no tags found
        return
    return reply.splitlines()[0].strip()

def repo_info(deps, progress, verbose, dry_run):
    """return a PathSource object with repository informations.
    """
    path_set= all_paths_from_deps(deps)
    new= utils.PathSource()
    cnt_max= 50
    cnt= 0
    if progress:
        utils.show_progress(cnt, cnt_max, "paths searched for darcs")
    for path in path_set:
        if progress:
            cnt= utils.show_progress(cnt, cnt_max)
        if not os.path.exists(os.path.join(path,"_darcs")):
            new.add_path(path)
            continue
        # try to find source repository:
        src= darcs_source_repo(path, verbose, dry_run)
        if not src:
            new.add_path(path)
            continue
        tag= darcs_last_tag(path, verbose, dry_run)
        if not tag:
            new.add_darcs(path, src)
            continue
        if not utils.is_standardpath(path, tag):
            new.add_darcs(path, src)
            continue
        new.add_darcs(path, src, tag)
    if progress:
        sys.stderr.write("\n")
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

def process(options, commands):
    """do all the work.

    known commands:
      deps
      repos
      groups
    """
    if not commands:
        sys.exit("command missing")
    for c in commands:
        if not c in KNOWN_COMMANDS:
            sys.exit("unknown command: %s" % c)

    deps= None

    if options.dir:
        deps= get_dependencies(options)
    elif options.info_file:
        deps= utils.json_loadfile(options.info_file)
    else:
        sys.exit("error: -d or -i required for command")

    if options.exclude_paths:
        deps= filter_exclude_paths(deps, options.exclude_paths)
    if options.exclude_deps:
        deps= filter_exclude_deps(deps, options.exclude_deps)

    bag= {}

    if "deps" in commands:
        bag["dependencies"]= deps
    if "name2paths" in commands:
        bag["name2paths"]= name2path_from_deps(deps)
    if "path2names" in commands:
        bag["path2names"]= path2name_from_deps(deps)
    if "groups" in commands:
        bag["groups"]= groups_from_deps(deps, options.group_basedir)
    if "repos" in commands:
        # a utils.PathSource object:
        repo_data= repo_info(deps,
                             options.progress,
                             options.verbose, options.dry_run)
        bag["repos"]= repo_data.to_dict()
        if options.missing_repo:
            bag["missing-repo"]= repo_data.filter_no_repos()
        if options.missing_tag:
            bag["missing-tag"]= repo_data.filter_no_tags()
    utils.json_dump(bag)

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
    usage = "usage: %prog [options] command\n" + \
            "where command is:\n" + \
            "  deps  : scan RELEASE files\n" + \
            "  repos : scan for repositories\n" + \
            "  groups: group directories by name\n" + \
            "  name2paths: return a map mapping names to paths\n" + \
            "  path2names: return a map mapping paths to names\n" + \
            "  groups: scan for groups\n\n" + \
            "commands can be combined!"

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
    parser.add_option("--group-basedir",
                      action="store", 
                      help="try to group directories by their name. The "+ \
                           "BASEDIR is taken as directory base to "+ \
                           "calculate group names from directory names",
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
    parser.add_option("--missing-tag",
                      action="store_true", 
                      help="show directories where a repository was "+ \
                           "found but no tag",
                      )
    parser.add_option("--missing-repo",
                      action="store_true", 
                      help="show directories where no repository was found",
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
    process(options, args)
    sys.exit(0)

if __name__ == "__main__":
    main()

