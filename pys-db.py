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
    for module_name, groupdata in groups.items():
        _taglesscnt=0
        _pathcnt= 0
        db_moduleversions= {}
        db[module_name] = db_moduleversions
        root_path= groupdata["path"]
        versions_from_path= groupdata["versions"]

        for version_from_path in sorted(versions_from_path):
            versionedmodule_path= os.path.join(root_path, version_from_path)
            modulesource_data= repoinfo.get(versionedmodule_path)
            if modulesource_data is None:
                errmsg("no source data: %s %s" % \
                       (module_name, version_from_path))
                continue
            if modulesource_data[0]=="path":
                versionname= "PATH-%03d" % _pathcnt
                _pathcnt+= 1
            elif modulesource_data[0]=="darcs":
                if len(modulesource_data)<3:
                    versionname= "TAGLESS-%03d" % _taglesscnt
                    _taglesscnt+= 1
                else:
                    versionname= modulesource_data[2]
            db_versionedmodule= {}
            db_moduleversions[versionname]= db_versionedmodule
            db_versionedmodule["source"]= modulesource_data

            _path2namevname[versionedmodule_path]= (module_name,versionname)
            _namevname2path[(module_name, versionname)]= versionedmodule_path

    for modulename, module in db.items():
        for versionname, versionedmodule in module.items():
            db_dependencies= {}
            versionedmodule["dependencies"]= db_dependencies
            versionedmodule_path= _namevname2path[(modulename, versionname)]
            _deps= deps.get(versionedmodule_path)
            if _deps is None:
                errmsg("no dependency info for path %s" % \
                       versionedmodule_path)
                continue
            for alias, dep_path in _deps.items():
                (_dep_name, _dep_version)= _path2namevname[dep_path]
                _l= [_dep_version]
                if _dep_name!=alias:
                    _l.append(alias)
                db_dependencies[_dep_name]= _l

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
    for dep_modulename, dep_data in versionedmodule["dependencies"].items():
        new_dist= _distribution_add(db, new_dist, dep_modulename, dep_data[0])
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
        repoinfo= utils.json_loadfile(options.repo_file)
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

    if options.test:
        _test()
        sys.exit(0)

    # we could pass "args" as an additional parameter to process here if it
    # would be needed to process remaining command line arguments.
    process(options)
    sys.exit(0)

if __name__ == "__main__":
    main()


