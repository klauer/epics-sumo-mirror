#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

# pylint: disable=C0322,C0103

from optparse import OptionParser
import sys
import os.path
import os

import pysupport_utils as utils

# version of the program:
my_version= "1.0"

def replace_paths(deps, repo_info):
    """replace all paths in deps with repository info from repo_info.
    """
    def conv_path(p):
        """create a universal path.
        """
        properties= repo_info.get(p)
        if not properties:
            return utils.uni_path([p])
        if len(properties)==2:
            # we cannot accept a repository without a tag here. If the tag is
            # missing, treat this as if there was no repository at all:
            return utils.uni_path([p])
        return utils.uni_path(properties)
    new= {}
    for path, dependencies in deps.items():
        d= {}
        for name, dep in dependencies.items():
            d[name]= conv_path(dep)
        new[conv_path(path)]= d
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
    if options.add_repo_info:
        if not options.dep_file:
            sys.exit("--dep-file is mandatory for this command")
        if not options.repo_file:
            sys.exit("--repo-file is mandatory for this command")
        deps= utils.json_loadfile(options.dep_file)
        repoinfo= utils.json_loadfile(options.repo_file)
        deps= replace_paths(deps, repoinfo)
        utils.json_dump(deps)
        return
    print "noting to do!"
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
    parser.add_option("-d","--dep-file",
                      action="store", 
                      type="string",  
                      help="read information from DEPENCYFILE. If "+ \
                           "DEPENCYFILE is \"-\" read from standard "+ \
                           "input.",
                      metavar="DEPENCYFILE"  
                      )
    parser.add_option("-r","--repo-file",
                      action="store", 
                      type="string",  
                      help="read information from REPOINFOFILE.",
                      metavar="REPOINFOFILE"  
                      )
    parser.add_option("--add-repo-info",
                      action="store_true", 
                      help="replace paths in DEPENCYFILE with repository "+ \
                           "specifications taken from REPOINFOFILE.",
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


