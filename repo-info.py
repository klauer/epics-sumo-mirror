#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

# pylint: disable=C0322,C0103

from optparse import OptionParser
import sys
import os.path
import os
import re

import pysupport_utils as utils

# version of the program:
my_version= "1.0"

# -----------------------------------------------
# small utilities
# -----------------------------------------------

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

# -----------------------------------------------
# RELEASE file scanning
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

# -----------------------------------------------
# darcs utilities
# -----------------------------------------------

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
    """return a dict with repository informations.
    """
    path_set= all_paths_from_deps(deps)
    new= {}
    cnt_max= 50
    cnt= 0
    if progress:
        utils.show_progress(cnt, cnt_max, "paths searched for darcs")
    for path in path_set:
        if progress:
            cnt= utils.show_progress(cnt, cnt_max)
        if not os.path.exists(os.path.join(path,"_darcs")):
            new[path]= ["path", path]
            continue
        # try to find source repository:
        src= darcs_source_repo(path, verbose, dry_run)
        if not src:
            new[path]= ["path", path]
            continue
        tag= darcs_last_tag(path, verbose, dry_run)
        if not tag:
            new[path]= ["darcs", src]
            continue
        if not is_standardpath(path, tag):
            new[path]= ["darcs", src]
            continue
        new[path]= ["darcs", src, tag]
    if progress:
        sys.stderr.write("\n")
    return new

def filter_no_repos(data):
    """leave only entries of type "path".
    """
    new= {}
    for path, lst in data.items():
        if lst[0]=="path":
            new[path]= lst
    return new

def filter_no_tags(data):
    """leave only entries where type!="path" and where the tag is missing.
    """
    new= {}
    for path, lst in data.items():
        if lst[0]=="path":
            continue
        if len(lst)<3:
            new[path]= lst
    return new

# -----------------------------------------------
# main
# -----------------------------------------------

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])


def process(options):
    """do all the work.
    """
    repo_data= None
    if options.dep_file:
        deps= utils.json_loadfile(options.dep_file)
        repo_data= repo_info(deps,
                             options.progress,
                             options.verbose, options.dry_run)
    elif options.info_file:
        repo_data= utils.json_loadfile(options.info_file)

    if not repo_data:
        required=["--info-file","--dep-file"]
        sys.exit("error, one of these options must be provided: %s" % \
                 (" ".join(required)))

    if options.missing_repo:
        repo_data= filter_no_repos(repo_data)
    if options.missing_tag:
        repo_data= filter_no_tags(repo_data)
    utils.json_dump(repo_data)
    return


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
    parser.add_option("-i","--info-file",
                      action="store", 
                      type="string",  
                      help="read information from INFOFILE. This is a "+ \
                           "generated by this script in a prevous run.",
                      metavar="INFOFILE"  
                      )
    parser.add_option("-d","--dep-file",
                      action="store", 
                      type="string",  
                      help="read information from DEPENCYFILE. If "+ \
                           "DEPENCYFILE is \"-\" read from standard "+ \
                           "input.",
                      metavar="DEPENCYFILE"  
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

    if options.test:
        _test()
        sys.exit(0)

    # we could pass "args" as an additional parameter to process here if it
    # would be needed to process remaining command line arguments.
    process(options)
    sys.exit(0)

if __name__ == "__main__":
    main()

