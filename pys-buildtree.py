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

KNOWN_COMMANDS=set(("newtree", "partialdb", "findtree"))

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

def builddb_match(db, builddb, modulename, versionname):
    """try to find matching deps in builddb.
    """
    deps= gather_dependencies(db, modulename, versionname)
    for build_tag in builddb.iter_builds():
        if not builddb.has_module(build_tag, modulename):
            continue
        if builddb.module_is_linked(build_tag, modulename):
            # if this build has only a link of the module, skip it
            continue
        modules= builddb.modules(build_tag)
        if modules[modulename]!=versionname:
            # version doesn't match
            continue

        # from here: check if all dependencies match:
        match= True
        for module_name, versionname in deps.items():
            other= modules.get(module_name)
            if versionname!= other:
                match= False
                break
        if match:
            return build_tag
    return

def gather_dependencies(db, modulename, versionname, 
                        gathered_deps= None):
    """recursively gather all dependencies of a module."""
    if gathered_deps is None:
        gathered_deps= {}
    for dep_name in db.iter_dependencies(modulename, versionname):
        dep_versions= list(db.iter_dependency_versions(modulename, 
                                                       versionname, 
                                                       dep_name))
        if len(dep_versions)>1:
            raise AssertionError, "m:%s v:%s d:%s" % \
                    (modulename, versionname, dep_name)
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

def gen_RELEASE(db, buildtag, modulename, versionname, epicsbase,
                verbose, dry_run):
    """generate a RELEASE file."""
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

    for dep_name in db.iter_dependencies(modulename, versionname):
        dep_versions= list(db.iter_dependency_versions(modulename, 
                                                       versionname, 
                                                       dep_name))
        dep_versionname= dep_versions[0]
        name_here= db.get_alias(modulename, versionname, dep_name)
        path= os.path.abspath(
                  module_dir_string(buildtag, dep_name, dep_versionname) 
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

def create_source(db, modulename, versionname, 
                  destdir, verbose, dry_run):
    """create directory by given source spec.
    """
    (type_, url, tag)= db.source(modulename, versionname)
    if type_=="path":
        #cmd= "scp -r -p \"%s\" %s" % (url, destdir)
        # join(url,"") effectively adds a "/" at the end of the path. This is
        # needed in order for rsync to work as intended here.
        cmd= "rsync -a -u -L \"%s\" %s" % (os.path.join(url,""), destdir)
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

def create_module(db, builddb, build_tag, 
                  modulename, versionname, 
                  epicsbase,
                  verbose, dry_run):
    """check out a module.

    returns the build_tag that was used. If the module was found in another
    build, return that built-tag.
    """
    basedir= module_basedir_string(modulename)
    ensure_dir(basedir, dry_run) # creates basedir if it doesn't exist
    dirname= module_dir_string(build_tag, modulename, versionname)
    if os.path.exists(dirname):
        raise ValueError, "directory %s already exists" % dirname

    compatible_build= builddb_match(db, builddb, modulename, versionname)
    if compatible_build:
        src_dirname= module_dir_string(compatible_build, 
                                       "", versionname)
        os.symlink(src_dirname, dirname)
        return compatible_build

    create_source(db, modulename, versionname, dirname, verbose, dry_run)
    gen_RELEASE(db, build_tag, modulename, versionname, 
                epicsbase,
                verbose, dry_run)
    return build_tag

def create_modules(db, builddb, build_tag, epicsbase, verbose, dry_run):
    """create all modules.
    """
    for modulename in db.iterate():
        moduleversions= list(db.iter_versions(modulename))
        if len(moduleversions)!=1:
            raise ValueError, "more than one version for %s" % modulename
        versionname= moduleversions[0]
        build_tag_used= \
            create_module(db, builddb, build_tag, 
                          modulename, versionname,
                          epicsbase,
                          verbose, dry_run)
        builddb.add_module(build_tag, build_tag_used, modulename, versionname)

def create_makefile(db, builddb, build_tag, verbose, dry_run):
    """generate a makefile.
    """
    def wr(fh, st, verbose):
        """write to file."""
        if verbose:
            print st,
        if fh:
            fh.write(st)
    paths= {}
    for modulename, versionname in builddb.iter_modules(build_tag):
        if not builddb.module_is_linked(build_tag, modulename):
            paths[(modulename, versionname)]= \
                         module_dir_string(build_tag, 
                                           modulename, 
                                           versionname)
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
        for dep_name in db.iter_dependencies(modulename, versionname):
            if builddb.module_is_linked(build_tag, dep_name):
                continue
            dep_versions= list(db.iter_dependency_versions(modulename, 
                                                           versionname, 
                                                           dep_name))
            dep_path= module_dir_string(build_tag, dep_name, dep_versions[0])
            dep_stamps.append(os.path.join(dep_path,"stamp"))

        if dep_stamps:
            wr(fh, "\n%s: %s\n" % (own_stamp, " ".join(dep_stamps)), verbose)
    wr(fh, "\n%/stamp:\n", verbose)
    wr(fh, "\tmake -C $(@D)\n", verbose)
    wr(fh, "\ttouch $@\n", verbose)
    if not dry_run:
        fh.close()

def create_partialdb(db, builddb, buildtag):
    """create a partial database from a build."""
    new= utils.Dependencies()
    for modulename, versionname in builddb.iter_modules(buildtag):
        new.copy_module_data(db, modulename, versionname)
    return new

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def process(options, commands):
    """do all the work.
    """
    if not commands:
        sys.exit("command missing")
    if commands[0] not in KNOWN_COMMANDS:
        sys.exit("unknown command: %s" % commands[0])

    if commands[0]=="newtree":
        if len(commands)>1:
            sys.exit("error: extra arguments following \"newtree\"")
        if not options.db:
            sys.exit("--db is mandatory")
        if not options.buildtag:
            sys.exit("--buildtag is mandatory")
        if not options.epicsbase:
            sys.exit("--epicsbase is mandatory")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        db= utils.Dependencies.from_json_file(options.db)
        builddb= utils.Builddb.from_json_file(options.builddb)
        if builddb.has_build_tag(options.buildtag):
            sys.exit("error, buildtag \"%s\" already taken" % options.buildtag)
        create_modules(db, builddb, options.buildtag, 
                       options.epicsbase,
                       options.verbose, options.dry_run)
        create_makefile(db, builddb, options.buildtag, 
                        options.verbose, options.dry_run)
        builddb.json_save(options.builddb, options.verbose, options.dry_run)
        return
    if commands[0]=="partialdb":
        if len(commands)>1:
            sys.exit("error: extra arguments following \"partialdb\"")
        if not options.db:
            sys.exit("--db is mandatory")
        if not options.buildtag:
            sys.exit("--buildtag is mandatory")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        db= utils.Dependencies.from_json_file(options.db)
        builddb= utils.Builddb.from_json_file(options.builddb)
        new_db= create_partialdb(db, builddb, options.buildtag)
        new_db.json_print()
        return
    if commands[0]=="findtree":
        if len(commands)<2:
            sys.exit("error: module specs missing")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        builddb= utils.Builddb.from_json_file(options.builddb)
        new_builddb= builddb.filter_by_spec(commands[1:])
        if not options.brief:
            new_builddb.json_print()
        else:
            if new_builddb.is_empty():
                print "no matching buildtrees found"
            else:
                print "matches:"
                d= {}
                for b in new_builddb.iter_builds():
                    d[b]= new_builddb.modules(b)
                utils.json_dump(d)
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

usage = """usage: %prog [options] command
where command is:
  newtree   : create a new buildtree
  partialdb : recreate a partial db from a complete db and an buildtree
  findtree [modules] :
              find buildtrees that have all the given modules.
"""

def main():
    """The main function.

    parse the command-line options and perform the command
    """
    # command-line options and command-line help:

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
    parser.add_option("--db", 
                      action="store", 
                      type="string",  
                      help="define the name of the DBFILE",
                      metavar="DBFILE"  
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
    parser.add_option("-b", "--brief", 
                      action="store_true", 
                      help="do a more brief output for some commands",
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
    process(options, args)
    sys.exit(0)

if __name__ == "__main__":
    main()



