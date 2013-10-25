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

SUPPORT= "/opt/repositories/controls/darcs/epics/support"

rx_darcs_root= re.compile(r'^\s*Root:\s*(.*)')
rx_darcs_repo= re.compile(r'^\s*Default Remote:\s*(.*)')

rx_darcs_repoline= \
        re.compile(r'(?:/darcs/epics|:darcs-repos/epics)/support/(.*)')

def json_dump(var):
    """Dump a variable in JSON format."""
    if json_type==0:
        print json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        print json.dumps(var, sort_keys= True, indent= 4)

# temporarily search modules in my local bii_scripts copy:
sys.path.insert(0, "/home/pfeiffer/net/project/bii_scripts/lib/python")

import makefile_scan

makefile_scan_pre= {}

# -----------------------------------------------
# small utilities
# -----------------------------------------------

def parse_support_path(path):
    """parses a support path.

    returns the generic support path and the version subdir.
    """
    (head, tail)= os.path.split(path)
    if not tail:
        return (None, None)
    if not tail[0].isdigit():
        return (None, None)
    return (head, tail)

def append_list_elm(dict_, key, val):
    """add a key, create a list if needed."""
    l= dict_.get(key)
    if l is None:
        dict_[key]= set([val])
    else:
        l.add(val)

def errprint(msg):
    """print a message to stderr."""
    sys.stderr.write(msg+"\n")

def versionedsupport_split(sup):
    """split a support in (path,version).
    """
    l= sup.strip().split("#")
    if len(l)>2:
        raise AssertionError, "unexpected support string: %s" % sup
    if len(l)<2:
        return (sup,"")
    return l

def versionedsupport_join(sup, ver):
    """join a support and version."""
    if not ver:
        return sup
    return "%s#%s" % (sup, ver)

def versionedsupport_has_version(sup):
    """returns True if there is a version."""
    return "#" in sup

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
    """get the darcs source repository."""
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
            default_repo= m.group(1).strip()
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
    m= rx_darcs_repoline.search(url)
    if not m:
        return url
    return "$SUPPORT/%s" % m.group(1)

def darcs_last_tag(directory, verbose, dry_run):
    """show the last given tag of the repo.
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

def darcs_info(directories, progress, verbose, dry_run):
    """return a dict with darcs informations.
    """
    new= {}
    cnt_max= 50
    cnt= 0
    if progress:
        sys.stderr.write(\
                "'.' for every %s directories searched for darcs\n" %\
                cnt_max)
    for d in directories:
        if progress:
            cnt-= 1
            if cnt<0:
                sys.stderr.write(".")
                sys.stderr.flush()
                cnt= cnt_max
        n= {}
        if os.path.exists(os.path.join(d,"_darcs")):
            src= darcs_source_repo(d, verbose, dry_run)
            tag= darcs_last_tag(d, verbose, dry_run)
            if src:
                n["repo"]= src
            if tag:
                # existence of "tag" implies existence of "repo":
                n["tag"]= tag
                n["standardpath"]= bool(d.endswith("/"+tag[1:]))
            else:
                n["standardpath"]= False
        new[d]= n
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
    versions_dict= calc_version_dict(deps)
    support_dict= {}
    remaining= []
    for support in supports:
        if not versionedsupport_has_version(support):
            remaining.append(support)
            continue
        _dependency_tree_add(support, support_dict, None)
        _dependency_tree(support, support_dict, None, deps)

    pprint.pprint(versions_dict)
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
            raise ValueError, ("no non-conflicting configuraion found "+ \
                    "(stopped at %s)") % support
        support_dict.update(d)
    lst= []
    for k,v in support_dict.items():
        lst.append(versionedsupport_join(k,v))
    return sorted(lst)

# pylint: disable=R0914,R0912

def rev2str(rev):
    """convert a revsion number to a comparable string."""
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

def calc_version_dict(deps):
    """find the newest version of a support.
    """
    cache= {}
    for k in deps.keys():
        (repo,tag)= versionedsupport_split(k)
        l= cache.get(repo)
        if l is None:
            l= []
            cache[repo]= l
        l.append(tag)
    for (k,l) in cache.items():
        cache[k]= sorted(l, key= rev2str, reverse= True)
        # newest versions first
    return cache

def dependency_data(support_tree, progress= False, 
                    verbose= False, dry_run= False):
    """scan a whole file-tree.
    """
    def slicer(l, val):
        """changes a list to a single element list"""
        try:
            i= l.index(val)
        except ValueError, _:
            return l
        l[i+1:]= []
        l[0:i]= []
        return l
    path2name= {}
    all_paths= set()
    dict_= {}
    cnt_max= 50
    cnt= 0
    if progress:
        sys.stderr.write(\
                "'.' for every %s directories searched for RELEASE\n" %\
                cnt_max)
    for (dirpath, dirnames, filenames) in os.walk(support_tree, topdown= True):
        if progress:
            cnt-= 1
            if cnt<0:
                sys.stderr.write(".")
                sys.stderr.flush()
                cnt= cnt_max
        slicer(dirnames, "configure")
        if os.path.basename(dirpath)=="configure":
            if "RELEASE" in filenames:
                # get the path of the versioned support:
                versioned_path= os.path.dirname(dirpath)
                data= scan_support_release(versioned_path,
                                           verbose= verbose, dry_run= dry_run)
                dict_[versioned_path]= data
                all_paths.add(versioned_path)
                for (name,path) in data.items():
                    (gen_path, _)= parse_support_path(path)
                    if not gen_path:
                        # version in path not parsable:
                        append_list_elm(path2name, path, name)
                    else:
                        append_list_elm(path2name, gen_path, name)
    name2path= {}
    for (path, namelist) in path2name.items():
        for n in namelist:
            append_list_elm(name2path, n, path)
    if progress:
        sys.stderr.write("\n")
    return (name2path, path2name, all_paths, dict_)

# pylint: enable=R0914,R0912

# -----------------------------------------------
# main
# -----------------------------------------------

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

# pylint: disable= R0912

def process(options,args):
    """do all the work.
    """
    def set2list(dict_):
        """change values from sets to sorted lists."""
        new= {}
        for (k,v) in dict_.items():
            new[k]= sorted(list(v))
        return new
    if options.make_distribution:
        if options.read_json:
            fh= open(options.read_json)
            results= json.load(fh)
            fh.close()
        else:
            if not options.parse_release:
                sys.exit("--parse_release is mandatory")
            (name2path, path2name, all_paths, dict_)= \
               dependency_data(options.parse_release,
                               options.progress,
                               options.verbose,
                               options.dry_run
                              )
            darcs_data= darcs_info(all_paths,
                                   options.progress,
                                   options.verbose, options.dry_run)
            dict_= deps2repospec(dict_, darcs_data)
            results["deps"]= dict_
        supports= sorted(options.make_distribution.split())
        result= { "required": supports,
                  "all" : dependency_tree(supports, results["deps"])
                }
        if options.json:
            json_dump(result)
        else:
            pprint.pprint(result)
        sys.exit(0)

    if options.parse_release:
        (name2path, path2name, all_paths, dict_)= \
           dependency_data(options.parse_release,
                           options.progress,
                           options.verbose,
                           options.dry_run
                          )
        results= {}
        darcs_data= None
        if options.darcs or options.deps_repospec:
            darcs_data= darcs_info(all_paths,
                                   options.progress,
                                   options.verbose, options.dry_run)
        if options.deps_repospec:
            dict_= deps2repospec(dict_, darcs_data)
        if options.name2paths:
            results["name2paths"]= set2list(name2path)
        if options.path2names:
            results["path2names"]= set2list(path2name)
        if options.darcs:
            results["darcs"]= darcs_data
        if options.deps:
            results["deps"]= dict_
        if options.json:
            json_dump(results)
        else:
            pprint.pprint(results)
    sys.exit(0)

# pylint: enable= R0912

def print_summary():
    """print a short summary of the scripts function."""
    print "%-20s: a tool for managing support EPICS trees \n" % \
          script_shortname()

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
    parser.add_option("--make-distribution",
                      action="store", 
                      type="string",  
                      help="MODULESPECS must be a space separated list "+\
                           "of modulespec strings. A modulespec string is "+\
                           "a path of a darcs repository with an optional "+\
                           "#tag appended",
                      metavar="DIR"  
                      )
    parser.add_option("--make-json",
                      action="store_true", 
                      help="implies --name2paths, --path2names, --deps, "+\
                           "--darcs --deps-repospec, --json",
                      )
    parser.add_option("--name2paths",   
                      action="store_true", 
                      help="show name2paths information",
                      )
    parser.add_option("--path2names",   
                      action="store_true", 
                      help="show path2names information",
                      )
    parser.add_option("--deps",   
                      action="store_true", 
                      help="show module dependencies",
                      )
    parser.add_option("--darcs",   
                      action="store_true", 
                      help="show darcs information for paths",
                      )
    parser.add_option("--deps-repospec",   
                      action="store_true", 
                      help="convert paths in deps (dependencies) to "+\
                           "repospecs (if possible)",
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

    if options.make_json:
        options.name2paths    = True
        options.path2names    = True
        options.deps          = True
        options.darcs         = True
        options.deps_repospec = True
        options.json          = True

    process(options,args)
    sys.exit(0)

if __name__ == "__main__":
    main()

