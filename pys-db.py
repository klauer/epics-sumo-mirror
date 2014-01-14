#! /usr/bin/env python2.5
# -*- coding: UTF-8 -*-
"""
=========
pys-db-py
=========

Create a JSON database with module and dependency information.

Logical definitions
-------------------

module:
    A module is a software package, usually an EPICS support module. Modules
    have a directory tree with the sources and are usually managed with a
    version control system. At the HZB we use darcs.  Each module has a unique
    *modulename*. The source of the module is available in several versions.
    The set of versions that have been tested are called the *moduleversions*.
    A single item of this set is called a *versionedmodule*.

versionedmodule:
    This is a named and tested version of a module. A versionedmodule has a
    *versionname* that is unique for that module, a *modulesource* and
    *dependencies*.

modulesource:
    This is the specification on how to obtain the module. The modulesource
    consists of a *sourcetype*, a *sourceurl* and an optional *sourcetag*.

dependencies:
    This is the specification of the dependencies of the versionedmodule. Each
    item is a *dependency*, consisting of a *modulename* and a *versionname*.
    Additionally, an *aliases* set defines alternative names for the dependency
    modules, these are needed for generation of configure/RELEASE files.

Datastructure
-------------

Some parts of the entities described above are used as keys in maps (python
dictionaries). In order to not to be confused with the definitions above we add
some more here.

dataset:
    This is the collection of all the module data, a map. In this map, each key
    is a *modulename* and the values are *moduleversions* entities.

modulename:
    The unique name of a module.

moduleversions:
    This is a map where each key is a *versionname* and each value is a
    *versiondata* item.

versiondata:
    This is a map that contains the information associated with the
    versionedmodile. The map keys are "source", the *modulesource* definition,
    "aliases", the alias map and "dependencies", the dependencies
    specification.

modulesource:
    This is the specification on how to obtain the module. It is a list of 2 to
    3 items. The first one is the *sourcetype*, the second one is the
    *sourceurl* and the optional third one is the *sourcetag*.

aliases:
    This is a map that contains optional alias names for modulenames in the
    dependency specification. These aliases may be needed for the generation of
    the configure/RELEASE files.

dependencies:
    This item contains the dependency specification for a module. It is a map
    where each key is a modulename and the value is a list of versionnames.


Example
-------

Here is an example of a dataset::

  {
      "ALARM": {
          "R3-5": {
              "dependencies": {
                  "MISC": [
                      "R2-4"
                  ],
                  "TIMER": [
                      "R5-1"
                  ]
              },
              "source": [
                  "darcs",
                  "/opt/repositories/controls/darcs/epics/support/alarm/base-3-14",
                  "R3-5"
              ]
          }
      },
  
      "MISC": {
          "R2-1": {
              "dependencies": {},
              "source": [
                  "darcs",
                  "/opt/repositories/controls/darcs/epics/support/misc/base-3-14",
                  "R2-1"
              ]
          },
          "R2-4": {
              "dependencies": {},
              "source": [
                  "darcs",
                  "/opt/repositories/controls/darcs/epics/support/misc/base-3-14",
                  "R2-4"
              ]
          }
      },
  }

"""

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

def script_shortname():
    """return the name of this script without a path component."""
    return os.path.basename(sys.argv[0])

def create_database(deps, repoinfo, groups):
    """join the information of the three sources.
    """
    def errmsg(msg):
        """print something on stderr."""
        sys.stderr.write(msg+"\n")

    _path2namevname= {}
    _namevname2path= {}
    db= {}
    # we first create the map from modulenames to versiondata. In this loop we
    # populate the versiondata only with the source specification. We also
    # create two maps:
    #    _path2namevname: maps a diretory path to (module_name, versionname)
    #    _namevname2path: maps (module_name,versionname) to a diretory path
    for module_name, groupdata in groups.items():
        _taglesscnt=0
        _pathcnt= 0
        db_moduleversions= {}
        db[module_name] = db_moduleversions
        # the root directory of all the versions:
        root_path= groupdata["path"]
        subdirs= groupdata["subdirs"]

        for subdir in sorted(subdirs):
            # iterate over all versions from <groups>:
            # reconstruct the original directory path:
            versionedmodule_path= os.path.join(root_path, subdir)
            # get the repository data:
            try:
                (source_type, _, source_tag) = \
                    repoinfo.get(versionedmodule_path)
            except KeyError, _:
                # shouldn't happen, but we just print a warning in this case:
                errmsg("no source data: %s" % versionedmodule_path)
                continue
            if source_type=="path":
                # the source is a directory path, not a repository. We generate
                # the unique versionname:
                versionname= "PATH-%03d" % _pathcnt
                _pathcnt+= 1
            elif source_type=="darcs":
                if not source_tag:
                    # the source is a darcs repository but has no tag. We
                    # generate a unique versionname:
                    versionname= "TAGLESS-%03d" % _taglesscnt
                    _taglesscnt+= 1
                else:
                    # the source is a darcs repository with a tag. We use the
                    # tag as unique versionname:
                    versionname= source_tag
            db_versionedmodule= {}
            db_moduleversions[versionname]= db_versionedmodule
            db_versionedmodule["source"]= \
                repoinfo.get_struct(versionedmodule_path)

            _path2namevname[versionedmodule_path]= (module_name,versionname)
            # when we assume that a versionedmodule_path may contain a
            # buildtag, there may be several versionedmodule_paths for a pair
            # of (module_name, versionname).
            _paths= _namevname2path.setdefault((module_name, versionname),[])
            _paths.append(versionedmodule_path)

    #utils.json_dump(_path2namevname)
    #sys.exit(0)

    # here we populate the versiondata with the dependency specifications:
    for modulename, module in db.items():
        for versionname, versionedmodule in module.items():
            db_aliases= {}
            versionedmodule_paths= _namevname2path[(modulename, versionname)]

            for versionedmodule_path in versionedmodule_paths:
                _deps= deps.get(versionedmodule_path)
                if _deps is None:
                    errmsg("no dependency info for path %s" % \
                           versionedmodule_path)
                    continue
                for alias, dep_path in _deps.items():
                    try:
                        (_dep_name, _dep_version)= _path2namevname[dep_path]
                    except KeyError, _:
                        sys.exit(("at module %s version %s "+ \
                                  "path %s: "+ \
                                  "missing data for "+ \
                                  "dependency \"%s\"") % \
                                  (modulename, versionname, 
                                   versionedmodule_path,
                                   dep_path))
                    if _dep_name != alias:
                        if db_aliases.has_key(_dep_name):
                            if db_aliases[_dep_name]!=alias:
                                errmsg(("multiple aliases in module %s: " + \
                                        "dependency %s aliases %s!=%s\n") % \
                                        (modulename, _dep_name, 
                                         db_aliases[_dep_name], alias))
                        else:
                            db_aliases[_dep_name]= alias
                    db_dependencies= \
                        versionedmodule.setdefault("dependencies", {})
                    _dep= db_dependencies.setdefault(_dep_name, [])
                    _dep.append(_dep_version)
            if db_aliases:
                versionedmodule["aliases"]= db_aliases
    return db

def _distribution_add(db, dist, modulename, versionname):
    """add a module to the set."""
    def _get_versionedmodule(db, modulename, versionname):
        """get the entry for modulename:versionname."""
        module= db.get(modulename)
        if module is None:
            return
        versionedmodule= module.get(versionname)
        if versionedmodule is None:
            return
        return versionedmodule
    versionedmodule= _get_versionedmodule(db, modulename, versionname)
    if versionedmodule is None:
        sys.exit("no information for module %s version %s" % \
                 (modulename, versionname))
    existing_versionname= dist.get(modulename)
    if existing_versionname is not None:
        if existing_versionname != versionname:
            raise ValueError, "conflict: %s %s %s" % \
                      (modulename, existing_versionname, versionname)
        return dist
    new_dist= dict(dist)
    new_dist[modulename]= versionname
    db_dependencies= versionedmodule.get("dependencies")
    if db_dependencies is None:
        return new_dist

    for dep_modulename, dep_data in db_dependencies.items():
        for dep_version in sorted(dep_data,
                                  key= utils.rev2key, reverse= True):
            errst= None
            try:
                new_dist= _distribution_add(db, 
                                            new_dist, 
                                            dep_modulename, 
                                            dep_version)
                errst= None
                break
            except ValueError, e:
                errst= str(e)
        if errst:
            raise ValueError, "last found %s" % errst
    return new_dist

def distribution(db, modulespecs):
    """create a distribution.
    """
    modulespec_list= modulespecs.split(",")
    versioned_modules= []
    versionless_modules= []
    for m in modulespec_list:
        l= m.split(":")
        if len(l)<=1:
            versionless_modules.append(l[0])
        else:
            versioned_modules.append(l)

    dist= {}
    for (modulename, versionname) in versioned_modules:
        try:
            dist= _distribution_add(db, dist, modulename, versionname)
        except ValueError, e:
            sys.exit(str(e))

    for modulename in versionless_modules:
        moduleversions= db.get(modulename)
        if moduleversions is None:
            sys.exit("no data for module %s" % modulename)
        versionnames= sorted(moduleversions.keys(),
                             key= utils.rev2key,
                             reverse= True)
        found= False
        for versionname in versionnames:
            try:
                dist= _distribution_add(db, dist, modulename, versionname)
                found= True
                break
            except ValueError, e:
                pass
        if not found:
            sys.exit("no non conflicting versions found for %s" % modulename)

    new= {}
    for (modulename, versionname) in dist.items():
        new[modulename]= { versionname: db[modulename][versionname] }
    return (dist,new)



def process(options):
    """do all the work.
    """
    if options.info_file:
        db= utils.json_loadfile(options.info_file)
    else:
        if not options.dep_file:
            sys.exit("--dep-file is mandatory for this command")
        if not options.repo_file:
            sys.exit("--repo-file is mandatory for this command")
        if not options.group_file:
            sys.exit("--group-file is mandatory for this command")

        deps= utils.json_loadfile(options.dep_file)
        repoinfo= utils.PathSource.from_json_file(options.repo_file)
        groups= utils.json_loadfile(options.group_file)

        db= create_database(deps, repoinfo, groups)

    if not options.distribution:
        utils.json_dump(db)
        return

    (dist_short, dist_long)= distribution(db, options.distribution)
    if options.brief:
        utils.json_dump(dist_short)
    else:
        utils.json_dump(dist_long)
    return

def print_doc():
    """print a short summary of the scripts function."""
    print __doc__

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
    parser.add_option("--doc",  
                      action="store_true", 
                      help="print a longer description of the program",
                      )
    parser.add_option("--test",  
                      action="store_true",
                      help="perform simple self-test", 
                      )
    parser.add_option("-i","--info-file",
                      action="store", 
                      type="string",  
                      help="read information from INFOFILE. This is a "+ \
                           "file generated by this script in a prevous run.",
                      metavar="INFOFILE"  
                      )
    parser.add_option("--distribution",
                      action="store", 
                      type="string",  
                      help="create a distribution from MODULESPECS. "+ \
                           "This is a comma separated list of "+ \
                           "NAME:VERSION pairs. If you want any version "+ \
                           "just specify NAME.",
                      metavar="MODULESPECS"  
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
    parser.add_option("-g","--group-file",
                      action="store", 
                      type="string",  
                      help="read information from GROUPFILE.",
                      metavar="GROUPFILE"  
                      )
    parser.add_option("-b", "--brief", 
                      action="store_true", 
                      help="create a more brief output",
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


