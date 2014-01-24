#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-

# pylint: disable=C0111
#                          Missing docstring
# pylint: disable=C0103
#                          Invalid name ... for type module
# pylint: disable=C0322
#                          Operator not preceded by a space

from optparse import OptionParser
import sys
import os.path
import os
import shutil

import pys_utils as utils

# version of the program:
my_version= "1.0"

KNOWN_COMMANDS=set(("show", "state", "newtree", "partialdb", "findtree", 
                    "apprelease", "fullapprelease", "delete"))

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

def gather_dependencies(db, modulename, versionname, 
                        gathered_deps= None):
    """recursively gather all dependencies of a module."""
    if gathered_deps is None:
        gathered_deps= {}
    for dep_name in db.iter_dependencies(modulename, versionname):
        # get all depdendencies, even ones marked "unstable":
        dep_versions= list(db.iter_dependency_versions(modulename, 
                                                       versionname, 
                                                       dep_name,
                                                       "unstable"))
        # Here we expect a unique version for each dependency of the module.
        if len(dep_versions)>1:
            raise AssertionError, "m:%s v:%s d:%s" % \
                    (modulename, versionname, dep_name)
        dep_version= dep_versions[0]
        existing= gathered_deps.get(dep_name)
        if existing is not None:
            if existing!=dep_version:
                raise AssertionError, \
                      "version conflict module %s versions %s %s" % \
                      (modulename, existing, dep_version)
            # if this is already in gathered_deps we can skip recursion here
            continue
        gathered_deps[dep_name]= dep_version
        gathered_deps= gather_dependencies(db, dep_name,  dep_version,
                                           gathered_deps)
    return gathered_deps

def _add_dependencies(module_dict, db, build_module_dict, 
                      modulename, versionname):
    """recursively add missing dependencies."""
    try:
        db.assert_module(modulename, versionname)
    except KeyError, e:
        sys.exit("%s in db file" % str(e))
    for dep in db.iter_dependencies(modulename, versionname):
        if module_dict.has_key(dep):
            continue
        version_present= build_module_dict[dep]
        if not db.depends_on(modulename, versionname, dep, version_present):
            str_= ("warning: dependency %s:%s is not in list "+ \
                   "of dependecies of module %s:%s in db file\n") % \
                   (dep,version_present,modulename,versionname)
            sys.stderr.write(str_)
        module_dict[dep]= version_present
        _add_dependencies(module_dict, db, build_module_dict,
                          dep, version_present)
        
def get_dependencies(module_dict, db, builddb, buildtag):
    """recursively complete the module_dict for missing dependencies."""
    build_module_dict= builddb.modules(buildtag)
    modules= module_dict.items()
    for modulename, versionname in modules:
        _add_dependencies(module_dict, db,
                          build_module_dict, modulename, versionname)

def builddb_match(db, builddb, modulename, versionname):
    """try to find matching deps in builddb.
    """
    deps= gather_dependencies(db, modulename, versionname)
    for build_tag in builddb.iter_builds():
        if not builddb.is_stable(build_tag):
            continue
        if not builddb.has_module(build_tag, modulename):
            continue
        if builddb.module_link(build_tag, modulename):
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

# pylint: disable=R0913
#                          Too many arguments
# pylint: disable=R0914
#                          Too many local variables

def gen_RELEASE(db, builddb, buildtag, modulename, versionname, 
                extra_lines,
                verbose, dry_run):
    """generate a RELEASE file."""
    def myprint(st):
        if verbose:
            print st,
        if not dry_run:
            fh.write(st)
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

    basedir= os.path.abspath(".")
    myprint("SUPPORT=%s\n" % basedir)
    for dep_name in db.iter_dependencies(modulename, versionname):
        # get all depdendencies, even ones marked "unstable":
        dep_versions= list(db.iter_dependency_versions(modulename, 
                                                       versionname, 
                                                       dep_name,
                                                       "unstable"))
        dep_versionname= dep_versions[0]
        name_here= db.get_alias(modulename, versionname, dep_name)
        buildtag_here= builddb.module_link(buildtag, dep_name)
        if buildtag_here is None:
            buildtag_here= buildtag
        path= os.path.join("$(SUPPORT)", 
                           module_dir_string(buildtag_here, dep_name, 
                                             dep_versionname) 
                          )
        myprint("%s=%s\n" % (name_here,path))
    for l in extra_lines:
        myprint("%s\n" % l.rstrip())
    if not dry_run:
        fh.close()

# pylint: enable=R0913
# pylint: enable=R0914

# pylint: disable=R0913
#                          Too many arguments

def create_source(db, modulename, versionname, 
                  destdir, verbose, dry_run):
    """create directory by given source spec.
    """
    (type_, url, tag)= db.module_source(modulename, versionname)
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

# pylint: enable=R0913

def delete_module(build_tag, modulename, versionname, 
                  verbose, dry_run):
    """delete a single module."""
    dirname= module_dir_string(build_tag, modulename, versionname)
    if verbose:
        print "removing %s" % dirname
    if not dry_run:
        shutil.rmtree(dirname)

def delete_modules(builddb, build_tag, verbose, dry_run):
    """delete modules of a build.
    """
    for b in builddb.iter_builds():
        if builddb.is_linked_to(b, build_tag):
            raise ValueError, "error: other builds depend on build %s" % \
                              build_tag
    for modulename, versionname in builddb.iter_modules(build_tag):
        if builddb.module_link(build_tag, modulename):
            continue
        delete_module(build_tag, modulename, versionname, verbose, dry_run)

    builddb.delete(build_tag)

# pylint: disable=R0913
#                          Too many arguments

def create_module(db, builddb, build_tag, 
                  modulename, versionname, 
                  extra_defs,
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

    create_source(db, modulename, versionname, dirname, verbose, dry_run)
    gen_RELEASE(db, builddb, build_tag, modulename, versionname, 
                extra_defs,
                verbose, dry_run)

# pylint: enable=R0913

def add_modules(db, builddb, build_tag):
    """add modules to the builddb object.
    """
    for modulename in db.iter_modulenames():
        moduleversions= list(db.iter_versions(modulename))
        if len(moduleversions)!=1:
            raise ValueError, "more than one version for %s" % modulename
        versionname= moduleversions[0]

        compatible_build= builddb_match(db, builddb, modulename, versionname)
        if compatible_build is None:
            build_tag_used= build_tag
        else:
            build_tag_used= compatible_build
        
        builddb.add_module(build_tag, build_tag_used, modulename, versionname)

# pylint: disable=R0913
#                          Too many arguments

def create_modules(partialdb, builddb, build_tag, extra_lines, 
                   verbose, dry_run):
    """create all modules.
    """
    add_modules(partialdb, builddb, build_tag)

    for modulename in partialdb.iter_modulenames():
        versionname= builddb.module_version(build_tag, modulename)
        # do not re-create modules that are links:
        if builddb.module_link(build_tag, modulename):
            continue
        create_module(partialdb, builddb, build_tag, 
                      modulename, versionname,
                      extra_lines,
                      verbose, dry_run)

# pylint: enable=R0913

# pylint: disable=R0914
#                          Too many local variables

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
        if not builddb.module_link(build_tag, modulename):
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
            if builddb.module_link(build_tag, dep_name):
                continue
            # get all depdendencies, even ones marked "unstable":
            dep_versions= list(db.iter_dependency_versions(modulename, 
                                                           versionname, 
                                                           dep_name,
                                                           "unstable"))
            dep_path= module_dir_string(build_tag, dep_name, dep_versions[0])
            dep_stamps.append(os.path.join(dep_path,"stamp"))

        if dep_stamps:
            wr(fh, "\n%s: %s\n" % (own_stamp, " ".join(dep_stamps)), verbose)
    wr(fh, "\n%/stamp:\n", verbose)
    wr(fh, "\tmake -C $(@D)\n", verbose)
    wr(fh, "\ttouch $@\n", verbose)
    if not dry_run:
        fh.close()

# pylint: enable=R0914

def create_partialdb(db, builddb, buildtag):
    """create a partial database from a build."""
    new= utils.Dependencies()
    for modulename, versionname in builddb.iter_modules(buildtag):
        new.import_module(db, modulename, versionname)
    return new

def fullapprelease(build_path, build_tag, module_dict, extra_lines):
    """create entries for an release file.
    """
    lines= ["SUPPORT=%s" % os.path.abspath(build_path)]
    for m in sorted(module_dict.keys()):
        basename= module_dir_string(build_tag, m, module_dict[m])
        lines.append("%s=%s" % \
                (m, 
                 os.path.join("$(SUPPORT)", basename)
                ))
    lines.extend(extra_lines)
    return "\n".join(lines)

# pylint: disable=R0913
#                          Too many arguments

def apprelease(build_path, build_tag, module_spec, builddb, db, extra_lines):
    """create entries for an release file.
    """
    build_modules= builddb.modules(build_tag)
    module_dict= {}
    for m in module_spec:
        (modulename,flag,versionname)= utils.scan_modulespec(m)
        v= build_modules.get(modulename)
        if v is None:
            sys.exit("error: module %s not found in build %s" % \
                     (modulename, build_tag))
        if versionname: # if versionname is given
            if not utils.compare_versions_flag(flag, v, versionname):
                sys.exit(("error: no module matching %s "+ \
                          "found in build %s") % (m, build_tag))
        module_dict[modulename]= v
    get_dependencies(module_dict, db, builddb, build_tag)
    return fullapprelease(build_path, build_tag, module_dict, extra_lines)

# pylint: enable=R0913

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

# pylint: disable=R0912
#                          Too many branches
# pylint: disable=R0911
#                          Too many return statements
# pylint: disable=R0915
#                          Too many statements

def process(options, commands):
    """do all the work.
    """
    if not commands:
        sys.exit("command missing")
    if commands[0] not in KNOWN_COMMANDS:
        sys.exit("unknown command: %s" % commands[0])

    if not options.extra:
        options.extra= []

    if commands[0]=="show":
        if len(commands)>2:
            sys.exit("error: extra arguments following \"show\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        buildtag= commands[1]
        builddb= utils.Builddb.from_json_file(options.builddb)
        if not builddb.has_build_tag(buildtag):
            sys.exit("error, buildtag \"%s\" not found" % buildtag)
        new_builddb= utils.Builddb()
        new_builddb.add_build(builddb, buildtag)
        new_builddb.json_print()
        return

    if commands[0]=="state":
        if len(commands)>3:
            sys.exit("error: extra arguments following \"state\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if len(commands)>2:
            if not options.db:
                sys.exit("--db is mandatory")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        buildtag= commands[1]
        if len(commands)>2:
            db= utils.Dependencies.from_json_file(options.db)
        else:
            db= None
        builddb= utils.Builddb.from_json_file(options.builddb)
        if not builddb.has_build_tag(buildtag):
            sys.exit("error, buildtag \"%s\" not found" % buildtag)
        if len(commands)<=2:
            print "%-20s : %s" % (buildtag, builddb.state(buildtag))
        else:
            new_state= utils.Builddb.guess_state(commands[2].strip())
            try:
                builddb.change_state(buildtag, new_state)
            except ValueError, e:
                sys.exit(str(e))
            builddb.json_save(options.builddb, 
                              options.verbose, options.dry_run)
            partialdb= create_partialdb(db, builddb, buildtag)
            db.merge(partialdb, new_state)
            db.json_save(options.db, options.verbose, options.dry_run)
        return

    if commands[0]=="delete":
        if len(commands)>2:
            sys.exit("error: extra arguments following \"delete\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        buildtag= commands[1]
        builddb= utils.Builddb.from_json_file(options.builddb)
        if not builddb.has_build_tag(buildtag):
            sys.exit("error, buildtag \"%s\" not found" % buildtag)
        try:
            delete_modules(builddb, buildtag, 
                           options.verbose, options.dry_run)
        except ValueError, e:
            sys.exit(str(e))
        builddb.json_save(options.builddb, 
                          options.verbose, options.dry_run)
        return

    if commands[0]=="newtree":
        if len(commands)>2:
            sys.exit("error: extra arguments following \"newtree\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if not options.db:
            sys.exit("--db is mandatory")
        if not options.partialdb:
            sys.exit("--partialdb is mandatory")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        buildtag= commands[1]
        db= utils.Dependencies.from_json_file(options.db)
        partialdb= utils.Dependencies.from_json_file(options.partialdb)
        builddb= utils.Builddb.from_json_file(options.builddb)
        if builddb.has_build_tag(buildtag):
            sys.exit("error, buildtag \"%s\" already taken" % buildtag)
        # create a new build in builddb, initial state is "unstable":
        builddb.new_build(buildtag, "unstable")
        # modifies builddb:
        create_modules(partialdb, builddb, buildtag, 
                       options.extra,
                       options.verbose, options.dry_run)
        create_makefile(partialdb, builddb, buildtag, 
                        options.verbose, options.dry_run)
        builddb.json_save(options.builddb, options.verbose, options.dry_run)
        db.merge(partialdb, "unstable")
        db.json_save(options.db, options.verbose, options.dry_run)
        return
    if commands[0]=="partialdb":
        if len(commands)>2:
            sys.exit("error: extra arguments following \"partialdb\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if not options.db:
            sys.exit("--db is mandatory")
        if not options.builddb:
            sys.exit("--builddb is mandatory")
        buildtag= commands[1]
        db= utils.Dependencies.from_json_file(options.db)
        builddb= utils.Builddb.from_json_file(options.builddb)
        new_db= create_partialdb(db, builddb, buildtag)
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
    if commands[0]=="fullapprelease":
        if len(commands)>2:
            sys.exit("error: extra arguments following \"fullapprelease\"")
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        buildtag= commands[1]
        builddb= utils.Builddb.from_json_file(options.builddb)
        print fullapprelease(os.path.dirname(options.builddb),
                             buildtag,
                             builddb.modules(buildtag),
                             options.extra)
        return
    
    if commands[0]=="apprelease":
        if len(commands)<=1:
            sys.exit("error: buildtag missing")
        if not options.db:
            sys.exit("--db is mandatory")
        buildtag= commands[1]
        modules= commands[2:]
        db= utils.Dependencies.from_json_file(options.db)
        builddb= utils.Builddb.from_json_file(options.builddb)
        print apprelease(os.path.dirname(options.builddb),
                         buildtag,
                         modules,
                         builddb,
                         db,
                         options.extra)
        return

# pylint: enable=R0912
# pylint: enable=R0911
# pylint: enable=R0915

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
  newtree [buildtag]  : 
          create a new buildtree
  partialdb [buildtag]: 
          recreate a partial db from a complete db and an buildtree
  findtree [modules] :
          find buildtrees that have all the given modules. Modules may have the
          form modulename or modulename:version or modulename:-version or
          modulename:+version
  fullapprelease [buildtag]: 
          create a RELEASE file for an application, use all the modules from
          the buildtree
  apprelease [buildtag] [modules]: create a RELEASE file for an application, 
          use only the mentioned modules and the modules they depend on. Note
          that --db is mandatory for this command.
  show [buildtag]
          show the data of the build
  state [buildtag] {new state}
          show or change the state of the build. Allowed states are "stable"
          and "testing".
  delete [buildtag] 
          delete the build if no other builds depend on it. Note that the build
          is kept in the build database but marked as "deleted".
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
    parser.add_option("-P", "--partialdb", 
                      action="store", 
                      type="string",  
                      help="define the name of the PARTIALDBFILE",
                      metavar="PARTIALDBFILE"  
                      )
    parser.add_option("--builddb",
                      action="store", 
                      type="string",  
                      help="specify the BUILDDATABASE",
                      metavar="BUILDDATABASE"  
                      )
    parser.add_option("-x", "--extra",
                      action="append", 
                      type="string",  
                      help="Extra lines that are added to the RELEASE "+ \
                           "file. A LINE may be an arbitrary string or "+ \
                           "definition.",
                      metavar="LINE"  
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

    # x= sys.argv
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



