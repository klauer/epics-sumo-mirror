#! /usr/bin/env python
# -*- coding: UTF-8 -*-

# pylint: disable=C0322,C0103

from optparse import OptionParser
import sys
import os.path
import os
import subprocess
import pprint
import re

if sys.version_info[0]>2 or (sys.version_info[0]==2 and sys.version_info[1]>5):
    import json
    json_type= 1
else:
    import simplejson as json
    json_type= 0

# version of the program:
my_version= "1.0"

IGNORE_NAMES= set(["TOP", "EPICS_BASE"])

# macros that are used to make paths more short and more unique:

# each list has 4 items:
# - regexp for macro resolution
# - replacement string for macro resolution
# - regexp for macro insertion
# - replacement string for macro insertion

MACROS= \
  { 
    "SUPPORT": 
      [
        re.compile(r'\$SUPPORT'),
        "/opt/repositories/controls/darcs/epics/support", # val
        re.compile(r'.*?(?:/darcs/epics|:darcs-repos/epics)/support(.*)'),
        r"$SUPPORT\1",
      ] 
  }

rx_darcs_root= re.compile(r'^\s*Root:\s*(.*)')
rx_darcs_repo= re.compile(r'^\s*Default Remote:\s*(.*)')

# temporarily search modules in my local bii_scripts copy:
sys.path.insert(0, "/home/pfeiffer/net/project/bii_scripts/lib/python")

import makefile_scan

makefile_scan_pre= {}

# -----------------------------------------------
# small utilities
# -----------------------------------------------

def use_macros(path):
    """try to replace parts in path with path MACROS.

    Here are some examples:
    >>> use_macros("rcsadm@aragon.acc:darcs-repos/epics/support/mba-templates/base-3-14")
    '$SUPPORT/mba-templates/base-3-14'
    >>> use_macros("/opt/repositories/controls/darcs/epics/support/mcan/base-3-14-8")
    '$SUPPORT/mcan/base-3-14-8'
    >>> use_macros("/srv/csr/Epics/R3.14.8/support/apsEvent/1-1")
    '/srv/csr/Epics/R3.14.8/support/apsEvent/1-1'
    """
    for l in MACROS.values():
        (_,_,rx,repl)= l
        path= re.sub(rx, repl, path)
    return path

def resolve_macros(path):
    """resolve macros used in path.

    Here are some examples:
    >>> resolve_macros("$SUPPORT/mba-templates/base-3-14")
    '/opt/repositories/controls/darcs/epics/support/mba-templates/base-3-14'
    >>> resolve_macros("$SUPPORT/mcan/base-3-14-8")
    '/opt/repositories/controls/darcs/epics/support/mcan/base-3-14-8'
    >>> resolve_macros("/srv/csr/Epics/R3.14.8/support/apsEvent/1-1")
    '/srv/csr/Epics/R3.14.8/support/apsEvent/1-1'
    """
    for l in MACROS.values():
        (rx,repl,_,_)= l
        path= re.sub(rx, repl, path)
    return path

def dict_of_sets_add(dict_, key, val):
    """add a key, create a list if needed.

    Here is an example:
    >>> d= {}
    >>> dict_of_sets_add(d,"a",1)
    >>> dict_of_sets_add(d,"a",2)
    >>> dict_of_sets_add(d,"b",1)
    >>> pprint.pprint(d)
    {'a': set([1, 2]), 'b': set([1])}
    """
    l= dict_.get(key)
    if l is None:
        dict_[key]= set([val])
    else:
        l.add(val)

def dict_sets_to_lists(dict_):
    """change values from sets to sorted lists.

    Here is an example:
    >>> d= {'a': set([1, 2]), 'b': set([1])}
    >>> ld= dict_sets_to_lists(d)
    >>> pprint.pprint(ld)
    {'a': [1, 2], 'b': [1]}
    """
    new= {}
    for (k,v) in dict_.items():
        new[k]= sorted(list(v))
    return new

def rev2str(rev):
    """convert a revsion number to a comparable string.

    This is needed to compare darcs revision tags.

    Here are some examples:
    >>> rev2str("R2-3-4")
    '002-003-004'
    >>> rev2str("head")
    '-head'
    >>> rev2str("test")
    '-test'
    >>> rev2str("test")<rev2str("R2-3-4")
    True
    >>> rev2str("R2-3-3")<rev2str("R2-3-4")
    True
    >>> rev2str("R2-3-5")<rev2str("R2-3-4")
    False
    >>> rev2str("R2-4-3")<rev2str("R2-3-4")
    False
    >>> rev2str("R1-3-4")<rev2str("R2-3-4")
    True
    >>> rev2str("R3-3-4")<rev2str("R2-3-4")
    False
    """
    if not rev: # empty string
        return "-"
    a= 0
    if not rev[a].isdigit():
        if len(rev)<=1:
            return "-"+rev
        a=1
    if not rev[a].isdigit():
        return "-"+rev
    l= rev[a:].split("-")
    n= []
    for e in l:
        try:
            n.append("%03d" % int(e))
        except ValueError, _:
            n.append(str(e))
    return "-".join(n)

def versionedsupport_split(sup):
    """split a versionedsupport in (path,version).

    Here are some examples:
    >>> versionedsupport_split("support/alarm#R2-2")
    ['support/alarm', 'R2-2']
    >>> versionedsupport_split("support/alarm")
    ('support/alarm', '')
    >>> versionedsupport_split("support/alarm#R2-2#3-4")
    Traceback (most recent call last):
        ...
    AssertionError: unexpected support string: support/alarm#R2-2#3-4
    """
    l= sup.strip().split("#")
    if len(l)>2:
        raise AssertionError, "unexpected support string: %s" % sup
    if len(l)<2:
        return (sup,"")
    return l

def versionedsupport_join(sup, ver):
    """join a support and version to a versionedsupport.

    Here are some examples:
    >>> versionedsupport_join("support/alarm", "R2-2")
    'support/alarm#R2-2'
    >>> versionedsupport_join("support/alarm", "")
    'support/alarm'
    >>> versionedsupport_join("support/alarm", None)
    'support/alarm'
    """
    if not ver:
        return sup
    return "%s#%s" % (sup, ver)

def versionedsupport_has_version(sup):
    """returns True if there is a version.

    Here are some examples:
    >>> versionedsupport_has_version("support/alarm#R2-2")
    True
    >>> versionedsupport_has_version("support/alarm")
    False
    """
    return "#" in sup

def is_standardpath(path, darcs_tag):
    """checks if path is complient to Bessy convention for support paths.
    
    Here are some examples:
    >>> is_standardpath("support/mcan/2-3", "R2-3")
    True
    >>> is_standardpath("support/mcan/2-3", "R2-4")
    False
    >>> is_standardpath("support/mcan/head", "R2-3")
    False
    """
    return path.endswith("/"+darcs_tag[1:])

def json_loadfile(filename):
    """load a JSON file.
    """
    fh= open(filename)
    results= json.load(fh)
    fh.close()
    return results

def json_dump(var):
    """Dump a variable in JSON format.

    Here is an example:
    >>> var= {"key":[1,2,3], "key2":"val", "key3":{"A":1,"B":2}}
    >>> json_dump(var)
    {
        "key": [
            1,
            2,
            3
        ],
        "key2": "val",
        "key3": {
            "A": 1,
            "B": 2
        }
    }
    """
    if json_type==0:
        print json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        print json.dumps(var, sort_keys= True, indent= 4)

def print_var(var, use_json= False):
    """print with either pprint or json.
    """
    if use_json:
        json_dump(var)
    else:
        pprint.pprint(var)


def show_progress(cnt, cnt_max, message= None):
    """show progress on stderr.
    """
    if message:
        sys.stderr.write("'.' for every %s %s\n" % (cnt_max, message))
    cnt-= 1
    if cnt<0:
        sys.stderr.write(".")
        sys.stderr.flush()
        cnt= cnt_max
    return cnt

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
# darcs utilities
# -----------------------------------------------

def darcs_source_repo(directory, verbose, dry_run):
    """get the darcs source repository.

    This function calls "darcs show repo". If there is a "Default
    repository" it is returned. If this is not presents the function
    returns "Root repository" as it is returned from darcs.
    """
    def _canonify(darcspath):
        """convert the darcspath to a real dictionary.
        """
        return resolve_macros(use_macros(darcspath))
    if not os.path.exists(os.path.join(directory,"_darcs")):
        return
    try:
        reply= _system("cd %s && darcs show repo" % directory, 
                       True, verbose, dry_run)
    except IOError, _:
        # probably no darcs repo found
        return
    root_repo= None
    default_repo= None
    for line in reply.splitlines():
        m= rx_darcs_repo.match(line)
        if m:
            r= _canonify(m.group(1).strip())
            if not os.path.exists(os.path.join(r,"_darcs")):
                continue
            default_repo= r
            continue
        m= rx_darcs_root.match(line)
        if m:
            root_repo= m.group(1).strip()
    if (not root_repo) and (not default_repo):
        return # repo not found
    url= root_repo
    if default_repo:
        url= default_repo
    #return url
    return use_macros(url)

def darcs_last_tag(directory, verbose, dry_run):
    """Returns the topmost darcs tag.
    """
    try:
        reply= _system("cd %s && darcs show tags" % directory, True, 
                       verbose, dry_run)
    except IOError, _:
        # probably no darcs repo found
        return
    if not reply:
        # no tags found
        return
    return reply.splitlines()[0].strip()

def darcs_info(deps, progress, verbose, dry_run):
    """return a dict with darcs informations.
    """
    directories= all_paths_from_deps(deps)
    new= {}
    cnt_max= 50
    cnt= 0
    if progress:
        show_progress(cnt, cnt_max, "directories searched for darcs")
    for d in directories:
        if progress:
            cnt= show_progress(cnt, cnt_max)
        n= {}
        if os.path.exists(os.path.join(d,"_darcs")):
            src= darcs_source_repo(d, verbose, dry_run)
            tag= darcs_last_tag(d, verbose, dry_run)
            if src:
                n["repo"]= src
            if tag:
                # existence of "tag" implies existence of "repo":
                n["tag"]= tag
                n["standardpath"]= is_standardpath(d, tag)
            else:
                n["standardpath"]= False
        new[d]= n
    if progress:
        sys.stderr.write("\n")
    return new

def path2repospec(p, darcs_data):
    """convert a support path to a canonical repo specification.
    """
    data= darcs_data.get(p)
    if not data:
        return p
    if not data["standardpath"]:
        return p
    # here we know that p ends with the *tag* string
    #print "DATA(",p,"):",repr(data)
    return versionedsupport_join(data["repo"], data["tag"])

def deps2repospec(deps, darcs_data):
    """convert all path in deps to repospec format."""
    new= {}
    for (k,v) in deps.items():
        n= {}
        new[path2repospec(k, darcs_data)]= n
        for (name, path) in v.items():
            n[name]= path2repospec(path, darcs_data)
    return new

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

def _dependency_tree_add(support, support_dict, old_support_dict):
    """add a single support to the support_dict.
    
    old_support_dict may be None
    """
    (repo, ver)= versionedsupport_split(support)
    existing= None
    if old_support_dict:
        existing= old_support_dict.get(repo)
    if not existing:
        existing= support_dict.get(repo)
    if not existing:
        support_dict[repo]= ver
    else:
        if existing!=ver:
            st= versionedsupport_join(repo, existing)
            raise ValueError, "version conflict: %s %s" % \
                    (st, support)

def _dependency_tree(support, support_dict, old_support_dict, deps):
    """recursively build a dependency tree.

    old_support_dict may be None
    """
    data= deps.get(support)
    if not data:
        return
    for (_, support_needed) in data.items():
        # may raise ValueError:
        _dependency_tree_add(support_needed, support_dict, old_support_dict)
        _dependency_tree(support_needed, support_dict, old_support_dict, deps)

def dependency_tree(supports, deps):
    """recursively build a dependency tree.
    """
    all_paths= all_paths_from_deps(deps)
    versions_dict= calc_version_dict(all_paths)
    support_dict= {}
    remaining= []
    for support in supports:
        if not versionedsupport_has_version(support):
            remaining.append(support)
            continue
        _dependency_tree_add(support, support_dict, None)
        _dependency_tree(support, support_dict, None, deps)

    # pprint.pprint(versions_dict)
    for support in remaining:
        success= False
        for ver in versions_dict[support]:
            s= versionedsupport_join(support, ver)
            d= {}
            try:
                _dependency_tree_add(s, d, support_dict)
                _dependency_tree(s, d, support_dict, deps)
                success= True
                break
            except ValueError, _:
                pass
        if not success:
            raise ValueError, ("no non-conflicting configuration found "+ \
                    "(stopped at %s)") % support
        support_dict.update(d)
    lst= []
    for k,v in support_dict.items():
        lst.append(versionedsupport_join(k,v))
    return sorted(lst)

def calc_version_dict(all_paths):
    """return a dict mapping repos to lists of versions.

    Returns a dictionary where the keys are repository paths and the values are
    ordered lists of darcs tags. Tags that are numbers are placed first in this
    sorted list.
    """
    support_versions= {}
    for p in all_paths:
        (repo,tag)= versionedsupport_split(p)
        dict_of_sets_add(support_versions, repo, tag)
    for (k,l) in support_versions.items():
        support_versions[k]= sorted(l, key= rev2str, reverse= True)
        # newest versions first
    return support_versions

# pylint: disable=R0914,R0912

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
        show_progress(cnt, cnt_max, "directories searched for RELEASE")
    for (dirpath, dirnames, filenames) in os.walk(support_tree, topdown= True):
        if progress:
            cnt= show_progress(cnt, cnt_max)
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

# pylint: enable=R0914,R0912

def all_paths_from_deps(deps):
    """get a collection of all paths from the dependency dict.
    """
    all_paths= set()
    for path, dependends in deps.items():
        all_paths.add(path)
        for dep_path in dependends.values():
            all_paths.add(dep_path)
    return all_paths

def name2path_from_deps(deps):
    """calculate name2path dict from dependency dict.
    """
    name2path= {}
    for dependends in deps.values():
        for name, dep_path in dependends.items():
            dict_of_sets_add(name2path, name, dep_path)
    return name2path

def path2name_from_deps(deps):
    """calculate path2name dict from dependency dict.
    """
    path2name= {}
    for dependends in deps.values():
        for name, dep_path in dependends.items():
            dict_of_sets_add(path2name, dep_path, name)
    return path2name

# -----------------------------------------------
# main
# -----------------------------------------------

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def get_dependencies(options, read_json, keep_darcs= False):
    """get the dependencies.
    """
    if read_json:
        return json_loadfile(options.read_json)
    else:
        if not options.parse_release:
            sys.exit("--parse_release is mandatory")
        deps= \
           dependency_data(options.parse_release,
                           options.progress,
                           options.verbose,
                           options.dry_run
                          )
        darcs_data= darcs_info(deps,
                               options.progress,
                               options.verbose, options.dry_run)
        # do always convert paths:
        deps= deps2repospec(deps, darcs_data)
        result= { "deps": deps }
        if keep_darcs:
            result["darcs"]= darcs_data
        return result


# pylint: disable= R0912,R0915

def process(options):
    """do all the work.
    """
    if options.list_supports:
        results= get_dependencies(options, options.read_json)
        all_paths= all_paths_from_deps(results["deps"])
        versions_dict= calc_version_dict(all_paths)
        result= sorted(versions_dict.keys())
        print_var(result, options.json)
        sys.exit(0)

    if options.calc_distribution or options.calc_distribution_by_file:
        results= get_dependencies(options, options.read_json)
        if options.calc_distribution:
            supports= sorted(options.calc_distribution.split())
        else:
            supports= json_loadfile(options.calc_distribution_by_file)
        result= { "required": supports,
                  "all" : dependency_tree(supports, results["deps"])
                }
        print_var(result, options.json)
        sys.exit(0)

    if options.parse_release:
        results= get_dependencies(
                          options, 
                          read_json= False,
                          keep_darcs= options.darcs)
        if options.name2paths:
            results["name2paths"]= \
                    dict_sets_to_lists(name2path_from_deps(results["deps"]))
        if options.path2names:
            results["path2names"]= \
                    dict_sets_to_lists(path2name_from_deps(results["deps"]))
        print_var(results, options.json)
    sys.exit(0)

# pylint: enable= R0912,R0915

def print_summary():
    """print a short summary of the scripts function."""
    print "%-20s: a tool for managing support EPICS trees \n" % \
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
                          description="This program manages EPICS support trees"
                         )

    parser.add_option("--summary",  
                      action="store_true", 
                      help="print a summary of the function of the program",
                      )
    parser.add_option("--test",  
                      action="store_true",
                      help="perform simple self-test", 
                      )
    parser.add_option("--parse-release", 
                      action="store", 
                      type="string",  
                      help="parse all RELEASE files in directory DIR",
                      metavar="DIR"  
                      )
    parser.add_option("--read-json", 
                      action="store", 
                      type="string",  
                      help="read information from JSONFILE",
                      metavar="JSONFILE"  
                      )
    parser.add_option("--calc-distribution",
                      action="store", 
                      type="string",  
                      help="MODULESPECS must be a space separated list "+\
                           "of modulespec strings. A modulespec string is "+\
                           "a path of a darcs repository with an optional "+\
                           "#tag appended",
                      metavar="DIR"  
                      )
    parser.add_option("--calc-distribution-by-file",
                      action="store", 
                      type="string",  
                      help="Make a distribution from the list of "+ \
                           "MODULESPECS listed in a JSONFILE.",
                      metavar="JSONFILE"  
                      )
    parser.add_option("--create-distribution-by-file",
                      action="store", 
                      type="string",  
                      help="Checkout a distribution by given JSONFILE "+ \
                           "containing MODULESPECS.",
                      metavar="JSONFILE"  
                      )
    parser.add_option("--list-supports",
                      action="store_true", 
                      help="Create a shortened list of support modules, "+\
                           "remove version tags if possible.",
                      )
    parser.add_option("--make-json",
                      action="store_true", 
                      help="implies --name2paths, --path2names "+\
                           "--darcs --json",
                      )
    parser.add_option("--name2paths",   
                      action="store_true", 
                      help="show name2paths information",
                      )
    parser.add_option("--path2names",   
                      action="store_true", 
                      help="show path2names information",
                      )
    parser.add_option("--darcs",   
                      action="store_true", 
                      help="show darcs information for paths",
                      )
    parser.add_option("-p", "--progress", 
                      action="store_true", 
                      help="show progress on stderr",
                      )
    parser.add_option("-j", "--json",   
                      action="store_true", 
                      help="print results in JSON format",
                      )
    parser.add_option("-r", "--raw",   
                      action="store_true", 
                      help="print results in RAW format (pprint)",
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

    if options.test:
        _test()
        sys.exit(0)

    if options.make_json:
        options.name2paths    = True
        options.path2names    = True
        options.darcs         = True
        options.json          = True

    # we could pass "args" as an additional parameter to process here if it
    # would be needed to process remaining command line arguments.
    process(options)
    sys.exit(0)

if __name__ == "__main__":
    main()

