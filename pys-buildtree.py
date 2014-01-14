#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

# pylint: disable=C0322,C0103

from optparse import OptionParser
import sys
import os.path
import os

import pys_utils as utils

# version of the program:
my_version= "1.0"

# -----------------------------------------------
# main
# -----------------------------------------------

def ensure_dir(dir_, dry_run):
    """create a dir if it doesn't already exist.
    """
    if not dry_run:
        if not os.path.exists(dir_):
            os.makedirs(dir_)

def module_dir_string(buildtag, modulename, versionname):
    """create a module directory string."""
    subdir= "%s+%s" % (versionname, buildtag)
    return os.path.join(modulename, subdir)

def module_basedir_string(modulename):
    """create a module base directory string."""
    return modulename

def errmsg(msg):
    """print something on stderr."""
    sys.stderr.write(msg+"\n")

def get_versioned_module(db, modulename, versionname):
    """return versionedmodule.

    exits the program in case of an error.
    """
    module= db.get(modulename)
    if module is None:
        sys.exit("no information found for module %s" % modulename)
    versionedmodule= module.get(versionname)
    if versionedmodule is None:
        sys.exit("no information found for module %s %s" % \
                 (modulename, versionname))
    return versionedmodule

def gather_dependencies(db, modulename, versionname, 
                        gathered_deps= None):
    """recursively gather all dependencies of a module."""
    if gathered_deps is None:
        gathered_deps= {}
    versionedmodule= get_versioned_module(db, modulename, versionname)
    deps= versionedmodule["dependencies"]
    for dep_name, dep_versions in deps.items():
        if len(dep_versions)>1:
            raise AssertionError, "m:%s v:%s d:%s" % \
                    (modulename, versionname, repr(deps))
        dep_version= dep_versions[0]
        gathered_deps[dep_name]= dep_version
        gathered_deps= gather_dependencies(db, dep_name,  dep_version,
                                           gathered_deps)
    return gathered_deps

def gather_all_dependencies(db):
    """gather all dependencies for a db.
    """
    deps= {}
    for modulename, moduleversions in db.items():
        if len(moduleversions.keys())!=1:
            raise AssertionError, "m:%s v:%s" % \
                     (modulename, repr(moduleversions))
        versionname= moduleversions.keys()[0]
        deps[modulename]= versionname
        deps= gather_dependencies(db, modulename, 
                                  versionname, deps)
    return deps

def add_builddb(db, builddb_file, buildtag, verbose, dry_run):
    """add an entry to the build database.
    """
    if os.path.exists(builddb_file):
        builddb= utils.json_loadfile(builddb_file)
    else:
        builddb= {}
    if builddb.has_key(buildtag):
        sys.exit("error, buildtag \"%s\" already taken" % buildtag)
    builddb[buildtag]= gather_all_dependencies(db)
    backup= "%s.bak" % builddb_file
    if os.path.exists(backup):
        if verbose:
            print "remove %s" % backup
        if not dry_run:
            os.remove(backup)
    if os.path.exists(builddb_file):
        if verbose:
            print "rename %s to %s" % (builddb_file, backup)
        if not dry_run:
            os.rename(builddb_file, backup)
    if not dry_run:
        utils.json_dump_file(builddb_file, builddb)

def gen_RELEASE(db, buildtag, modulename, versionname, epicsbase,
                verbose, dry_run):
    """generate a RELEASE file."""
    versionedmodule= get_versioned_module(db, modulename, versionname)
    dependencies= versionedmodule["dependencies"]
    dir_= module_dir_string(buildtag, modulename, versionname)
    config_dir= os.path.join(dir_, "configure")
    if not dry_run:
        if not os.path.exists(config_dir):
            errmsg("no configure directory found in %s" % dir_)
            return
    filename= os.path.join(config_dir, "RELEASE")
    if verbose:
        print "creating %s" % filename
    if not dry_run:
        fh= open(filename, "w")

    aliases= versionedmodule.get("aliases")
    for depname, dep_data in dependencies.items():
        dep_versionname= dep_data[0]
        name_here= None
        if aliases:
            name_here= aliases.get(depname)
        if not name_here:
            name_here= depname
        path= os.path.abspath(
                  module_dir_string(buildtag, depname, dep_versionname) 
                             )
        str_= "%s=%s\n" % (name_here,path)
        if verbose:
            print str_,
        if not dry_run:
            fh.write(str_)
    str_= "EPICS_BASE=%s\n" % epicsbase
    if verbose:
        print str_,
    if not dry_run:
        fh.write(str_)
    if not dry_run:
        fh.close()

def create_source(source_data, destdir, verbose, dry_run):
    """create directory by given source spec.
    """
    type_= source_data[0]
    url  = source_data[1]
    tag  = None
    if len(source_data)>2:
        tag= source_data[2]
    if type_=="path":
        cmd= "scp -r -p \"%s\" %s" % (url, destdir)
        utils.system(cmd, False, verbose, dry_run)
    elif type_=="darcs":
        cmd_l= ["darcs", "get"]
        if tag:
            cmd_l.extend(["-t", tag])
        cmd_l.append(url)
        cmd_l.append(destdir)
        cmd= " ".join(cmd_l)
        utils.system(cmd, False, verbose, dry_run)
    else:
        raise AssertionError, "unsupported source type %s" % type_

def create_module(db, build_tag, 
                  modulename, versionname, 
                  epicsbase,
                  verbose, dry_run):
    """check out a module."""
    versionedmodule= get_versioned_module(db, modulename, versionname)
    basedir= module_basedir_string(modulename)
    ensure_dir(basedir, dry_run)
    dirname= module_dir_string(build_tag, modulename, versionname)
    if os.path.exists(dirname):
        raise ValueError, "directory %s already exists" % dirname
    modulesource_data= versionedmodule["source"]
    create_source(modulesource_data, dirname, verbose, dry_run)
    gen_RELEASE(db, build_tag, modulename, versionname, 
                epicsbase,
                verbose, dry_run)

def create_makefile(db, build_tag, verbose, dry_run):
    """generate a makefile.
    """
    def wr(fh, st, verbose):
        """write to file."""
        if verbose:
            print st,
        if fh:
            fh.write(st)
    paths= {}
    for modulename, moduleversions in db.items():
        if len(moduleversions.keys())!=1:
            raise ValueError, "more than one version for %s" % modulename
        versionname= moduleversions.keys()[0]
        paths[(modulename, versionname)]= \
                     module_dir_string(build_tag, 
                                       modulename, 
                                       moduleversions.keys()[0])
    filename= "Makefile-%s" % build_tag
    stamps= sorted([os.path.join(p,"stamp") for p in paths.values()])
    fh= None
    if not dry_run:
        fh= open(filename, "w")
    wr(fh, "all: %s\n\n" % (" ".join(stamps)), verbose)
    wr(fh, "clean:\n", verbose)
    for f in stamps:
        wr(fh, "\trm %s\n" % f, verbose)
    wr(fh, "\n", verbose)
    for spec, path in paths.items():
        (modulename, versionname)= spec
        own_stamp= os.path.join(path, "stamp")
        dep_stamps= []
        for dep_name, dep_spec in \
                db[modulename][versionname]["dependencies"].items():
            dep_path= module_dir_string(build_tag, dep_name, dep_spec[0])
            dep_stamps.append(os.path.join(dep_path,"stamp"))
        if dep_stamps:
            wr(fh, "\n%s: %s\n" % (own_stamp, " ".join(dep_stamps)), verbose)
    wr(fh, "\n%/stamp:\n", verbose)
    wr(fh, "\tmake -C $(@D)\n", verbose)
    wr(fh, "\ttouch $@\n", verbose)
    if not dry_run:
        fh.close()

def create_modules(db, build_tag, epicsbase, verbose, dry_run):
    """create all modules.
    """
    for modulename, moduleversions in db.items():
        if len(moduleversions.keys())!=1:
            raise ValueError, "more than one version for %s" % modulename
        create_module(db, build_tag, 
                      modulename, moduleversions.keys()[0],
                      epicsbase,
                      verbose, dry_run)

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def process(options):
    """do all the work.
    """
    if not options.distribution:
        sys.exit("--distribution is mandatory")
    if not options.buildtag:
        sys.exit("--buildtag is mandatory")
    if not options.epicsbase:
        sys.exit("--epicsbase is mandatory")
    if not options.builddb:
        sys.exit("--builddb is mandatory")
    db= utils.json_loadfile(options.distribution)
    create_modules(db, options.buildtag, options.epicsbase,
                   options.verbose, options.dry_run)
    create_makefile(db, options.buildtag, 
                    options.verbose, options.dry_run)
    add_builddb(db, options.builddb, options.buildtag,
                options.verbose, options.dry_run)

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
    parser.add_option("-d", "--distribution",
                      action="store", 
                      type="string",  
                      help="create a build-tree from a DISTRIBUTION "+\
                           "file.",
                      metavar="DISTRIBUTION"  
                      )
    parser.add_option("-t", "--buildtag",
                      action="store", 
                      type="string",  
                      help="specify the BUILDTAG"+\
                           "file.",
                      metavar="BUILDTAG"  
                      )
    parser.add_option("--builddb",
                      action="store", 
                      type="string",  
                      help="specify the BUILDDATABASE",
                      metavar="BUILDDATABASE"  
                      )
    parser.add_option("--epicsbase",
                      action="store", 
                      type="string",  
                      help="specify the EPICSBASE",
                      metavar="EPICSBASE"  
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



