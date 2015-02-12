"""Database file handling.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys
import copy

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import sumolib.ModuleSpec
import sumolib.JSON
import sumolib.utils

__version__="2.4.3" #VERSION#

assert __version__==sumolib.ModuleSpec.__version__
assert __version__==sumolib.JSON.__version__
assert __version__==sumolib.utils.__version__

# -----------------------------------------------
# class definitions
# -----------------------------------------------

class DB(sumolib.JSON.Container):
    """the dependency database."""
    # pylint: disable=R0904
    #                          Too many public methods
    # pylint: disable=R0913
    #                          Too many arguments
    @staticmethod
    def check_arch(arch_dict, arch_list):
        """check if all arch_list elements are keys in arch_dict."""
        if arch_list is None:
            return True
        # special architecture "ANY" means than any architecture is supported.
        if arch_dict.get("ANY"):
            return True
        for a in arch_list:
            if not arch_dict.get(a):
                return False
        return True
    def selfcheck(self, msg):
        """raise exception if obj doesn't look like a dependency database."""
        def _somevalue(d):
            """return kind of arbitrary value of a dict."""
            keys= d.keys()
            key= keys[len(keys)/2]
            return d[key]
        while True:
            d= self.datadict()
            if not isinstance(d, dict):
                break
            module= _somevalue(d)
            if not isinstance(module, dict):
                break
            version= _somevalue(module)
            if not isinstance(version, dict):
                break
            deps= version.get("dependencies")
            if deps is not None:
                if not isinstance(deps, list):
                    break
            src= version.get("source")
            if not src:
                break
            return
        raise ValueError("error: dependency data is invalid %s" % msg)
    def __init__(self, dict_= None):
        """create the object."""
        super(DB, self).__init__(dict_)
    def merge(self, other):
        """merge another Dependencies object to self.

        parameters:
            self  - the object itself
            other - the other Dependencies object
        """
        # pylint: disable=R0912
        #                          Too many branches
        for modulename in other.iter_modulenames():
            m= self.datadict().setdefault(modulename,{})
            # iterate on stable, testing and unstable versions:
            for versionname in other.iter_versions(modulename,
                                                   None, False):
                vdict = m.setdefault(versionname,{})
                vdict2= other.datadict()[modulename][versionname]
                for dictname, dictval in vdict2.items():
                    if dictname=="archs":
                        try:
                            sumolib.utils.dict_update(\
                                        vdict.setdefault(dictname,{}),
                                        dictval)
                        except ValueError, e:
                            raise ValueError(\
                              "module %s version %s archs: %s" % \
                              (modulename, versionname, str(e)))
                        continue
                    if dictname=="weight":
                        # take the weight from the new dict if present
                        vdict[dictname]= dictval
                        continue
                    if dictname=="aliases":
                        try:
                            sumolib.utils.dict_update(\
                                        vdict.setdefault(dictname,{}),
                                        dictval)
                        except ValueError, e:
                            raise ValueError(\
                              "module %s version %s aliases: %s" % \
                              (modulename, versionname, str(e)))
                        continue
                    if dictname=="source":
                        if not vdict.has_key(dictname):
                            vdict[dictname]= vdict2[dictname]
                            continue
                        if vdict[dictname]!=vdict2[dictname]:
                            raise ValueError(
                                "module %s version %s source: "
                                "contradiction %s %s" % \
                                (modulename, versionname,
                                 repr(vdict[dictname]),
                                 repr(vdict2[dictname])))
                        continue
                    if dictname=="dependencies":
                        if not vdict.has_key(dictname):
                            vdict[dictname]= sorted(vdict2[dictname])
                            continue
                        if set(vdict[dictname])!=set(vdict2[dictname]):
                            raise ValueError(
                                "module %s version %s dependencies: "
                                "contradiction %s %s" % \
                                (modulename, versionname,
                                 repr(vdict[dictname]),
                                 repr(vdict2[dictname])))
                        continue
                    raise AssertionError("unexpected dictname %s" % dictname)
    def import_module(self, other, module_name, versionname):
        """copy the module data from another Dependencies object.

        This does a deepcopy of the data.
        """
        m= self.datadict().setdefault(module_name,{})
        m[versionname]= copy.deepcopy(\
                            other.datadict()[module_name][versionname])
    def set_source_spec(self, module_name, versionname, sourcespec):
        """set sourcespec of a module, creates if it does not yet exist.

        returns True if the spec was changed, False if it wasn't.
        """
        if not isinstance(sourcespec, sumolib.repos.SourceSpec):
            raise TypeError("error: sourcespec '%s' is of wrong "
                            "type" % repr(sourcespec))
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        old_source= version.get("source")
        if old_source is None:
            version["source"]= sourcespec.to_dict()
            return True
        old_spec= sumolib.repos.SourceSpec(old_source)
        return old_spec.change_source(sourcespec)
    def set_source_spec_by_tag(self, module_name, versionname, tag):
        """try to change sourcespec by providing a tag.

        returns True if the spec was changed, False if it wasn't.
        """
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        old_source= version.get("source")
        if old_source is None:
            raise ValueError("error, %s:%s source specification is empty, "
                             "cannot simply change the tag." % \
                             (module_name, versionname))
        old_spec= sumolib.repos.SourceSpec(old_source)
        try:
            ret= old_spec.change_source_by_tag(tag)
        except ValueError, e:
            raise ValueError("error, %s:%s %s" % \
                             (module_name, versionname, str(e)))
        version["source"]= old_spec.to_dict()
        return ret

    def set_source_arch(self, module_name, versionname, archs,
                        sourcespec):
        """add a module with source spec and archs."""
        if not isinstance(sourcespec, sumolib.repos.SourceSpec):
            raise TypeError("error: sourcespec '%s' is of wrong "
                            "type" % repr(sourcespec))
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        arch_dict= version.setdefault("archs", {})
        for arch in archs:
            arch_dict[arch]= True
        version["source"]= sourcespec.to_dict()
    def add_dependency(self, modulename, versionname,
                       dep_modulename):
        """add dependency for a module:version.
        """
        m_dict= self.datadict()[modulename]
        dep_list= m_dict[versionname].setdefault("dependencies",[])
        dep_list.append(dep_modulename)
        dep_list.sort()
    def del_dependency(self, modulename, versionname,
                       dep_modulename):
        """delete dependency for a module:version if it exists.
        """
        m_dict= self.datadict()[modulename]
        dep_list= m_dict[versionname].get("dependencies")
        if dep_list is None:
            raise ValueError("error: %s:%s has no dependencies" % \
                             (modulename, versionname))
        dep_set= set(dep_list)
        if not dep_modulename in dep_set:
            raise ValueError("error: %s:%s doesn't depend on %s" % \
                             (modulename, versionname, dep_modulename))
        dep_set.discard(dep_modulename)
        if not dep_set:
            # "dependencies" is now empty, remove it:
            del m_dict[versionname]["dependencies"]
        else:
            m_dict[versionname]["dependencies"]= sorted(list(dep_set))
    def check(self):
        """do a consistency check on the db."""
        msg= []
        for modulename in self.iter_modulenames():
            for versionname in self.iter_versions(modulename,
                                                  None, True):
                archs= self.get_archs(modulename, versionname).keys()
                if len(archs)==0:
                    msg.append("%s:%s: no target architectures" % \
                               (modulename, versionname))
                for dep_modulename in self.iter_dependencies(modulename,
                                                             versionname):
                    try:
                        self.assert_module(dep_modulename, None)
                    except KeyError, e:
                        msg.append("%s:%s: dependencies: %s" % \
                                (modulename, versionname, str(e)))
        return msg
    def search_modules(self, rx_object, archs):
        """search module names and source URLS for a regexp.

        Returns a list of tuples (modulename, versionname).
        """
        results= []
        for modulename in self.iter_modulenames():
            if rx_object.search(modulename):
                for versionname in self.iter_versions(modulename,
                                                      archs, False):
                    results.append((modulename, versionname))
                continue
            for versionname in self.iter_versions(modulename,
                                                  archs, False):
                repr_st= self.module_source_string(modulename, versionname)
                if rx_object.search(repr_st):
                    results.append((modulename, versionname))
        return sorted(results)
    def get_archs(self, modulename, versionname):
        """get archs for modulename:versionname."""
        m_dict= self.datadict()[modulename]
        return m_dict[versionname]["archs"]
    def check_archs(self, modulename, versionname, archs):
        """return True if all archs are supported in the module."""
        # pylint: disable=W0212
        #                          Access to a protected member of a
        #                          client class
        return self.__class__.check_arch(\
                   self.get_archs(modulename, versionname), archs)
    def add_alias(self, modulename, versionname,
                  alias_name, real_name):
        """add an alias for modulename:versionname."""
        m_dict= self.datadict()[modulename]
        alias_dict= m_dict[versionname].setdefault("aliases",{})
        if alias_dict.has_key(real_name):
            if alias_dict[real_name]==alias_name:
                return
            raise ValueError(\
                  "alias \"%s\" defined with two different names" % alias_name)
        alias_dict[real_name]= alias_name
    def get_alias(self, modulename, versionname,
                  dep_modulename):
        """return the alias or the original name for dep_modulename."""
        a_dict= self.datadict()[modulename][versionname].get("aliases")
        if a_dict is None:
            return dep_modulename
        return a_dict.get(dep_modulename, dep_modulename)
    def weight(self, modulename, versionname, new_weight= None):
        """set the weight factor."""
        if new_weight is None:
            return self.datadict()[modulename][versionname].get("weight", 0)
        if not isinstance(new_weight, int):
            raise TypeError("error: %s is not an integer" % repr(new_weight))
        self.datadict()[modulename][versionname]["weight"]= new_weight
    def assert_module(self, modulename, versionname):
        """do nothing if the module is found, raise KeyError otherwise.

        If versionname is None, just check that the modulename is known.
        """
        d= self.datadict().get(modulename)
        if d is None:
            raise KeyError("no data for module %s" % modulename)
        if versionname is None:
            return
        v= d.get(versionname)
        if v is None:
            raise KeyError("version %s not found for module %s" % \
                    (versionname, modulename))
    def dependencies_found(self, modulename, versionname):
        """returns True if dependencies are found for modulename:versionname.
        """
        # may raise KeyError exception in this line:
        d= self.datadict()[modulename][versionname]
        return d.has_key("dependencies")
    def module_source_dict(self, modulename, versionname):
        """return a dict {type:dict} for the module source."""
        return self.datadict()[modulename][versionname]["source"]
    def module_source_pair(self, modulename, versionname):
        """return a tuple (type,dict) for the module source."""
        l= self.datadict()[modulename][versionname]["source"]
        return sumolib.utils.single_key_item(l)
    def module_source_string(self, modulename, versionname):
        """return the source url or tar-file or path for a module."""
        (tp,val)= self.module_source_pair(modulename, versionname)
        if tp not in sumolib.repos.known_sources:
            raise AssertionError("unexpected source tag %s at %s:%s" % \
                    (tp, modulename, versionname))
        # due to variety of source specs, just return the "repr" string here:
        return repr(val)
    def iter_dependencies(self, modulename, versionname):
        """return an iterator on dependency modulenames of a module."""
        md= self.datadict().get(modulename)
        if md is None:
            raise KeyError("error: module %s not found in dependency "
                           "database" % modulename)
        d= md.get(versionname)
        if d is None:
            raise KeyError("error: module %s:%s not found in dependency "
                           "database" % (modulename,versionname))
        d= self.datadict()[modulename][versionname]
        deps= d.get("dependencies")
        if deps is None:
            return iter([])
        return iter(deps)
    def depends_on_module(self, modulename, versionname,
                          dependencyname):
        """returns True if given dependency is found.
        """
        d= self.datadict()[modulename][versionname]
        deps= d.get("dependencies")
        if deps is None:
            return False
        return dependencyname in deps
    def assert_complete_modulelist(self, moduledict):
        """test if a set of modules is complete.

        This means that all dependencies are part of the given modules.

        moduledict is a dictionary mapping modulename-->versionname.
        """
        missing= set()
        for modulename,versionname in moduledict.items():
            for dep in self.iter_dependencies(modulename, versionname):
                if not moduledict.has_key(dep):
                    missing.add(dep)
        if missing:
            raise ValueError("error: set of modules is incomplete, these "
                             "modules are missing: %s" % (" ".join(missing)))
    def sortby_weight(self, moduleversions, reverse= False):
        """sorts modules by weight.

        Order in a way that smaller weights come first.

        moduleversions: a list of pairs (modulename, versionname).
        """
        local_weights= {}
        i=0
        for m in moduleversions:
            local_weights[m]= i
            if reverse:
                i-=1
            else:
                i+= 1
        # now a list of tuples (weight,localweight,moduletuple) can easily be
        # sorted:
        sort_list= sorted([(self.weight(m[0],m[1]), local_weights[m], m) \
                           for m in moduleversions],
                          reverse= reverse)
        # created a list of moduletuples from the result:
        return [m for (_,_,m) in sort_list]

    def sortby_dependency(self, moduleversions, reverse= False):
        """sorts modules by dependencies.

        Order that dependent modules come *after* the modules they depend on.

        moduleversions: a list of pairs (modulename, versionname).
        """
        # pylint: disable=R0914
        #                          Too many local variables
        # pylint: disable=R0912
        #                          Too many branches
        module_version_dict= dict(moduleversions)
        dependencies= {}
        weights= {}
        i=0
        for m in moduleversions:
            weights[m]= i
            i+= 1

        # collect all direct dependencies:
        modules_set= set(moduleversions)

        # dependencies will map (modulename,versionname)->set(deps)
        # with each dep: (dep_name, dep_version)
        # we also include indirect dependencies, but only those that
        # are part of the given moduleversions parameter.
        test_modules_set= modules_set
        while test_modules_set:
            new_modules_set= set()
            for (modulename, versionname) in test_modules_set:
                s= dependencies.setdefault((modulename,versionname), set())
                for dep_name in self.iter_dependencies(modulename,
                                                       versionname):
                    # ignore dependencies that are not part of the given
                    # moduleversions parameter:
                    if not module_version_dict.has_key(dep_name):
                        continue
                    dep_version= module_version_dict[dep_name]
                    s.add((dep_name,dep_version))
                    new_modules_set.add((dep_name, dep_version))
            test_modules_set= new_modules_set

        # ensure that the "weight" of a module is always bigger than the
        # biggest weight of any of it's dependencies:
        changes= True
        while changes:
            changes= False
            for m in modules_set:
                deps= dependencies[m]
                if not deps:
                    continue
                maxweight= max([weights[mod] for mod in deps])
                if maxweight>= weights[m]:
                    changes= True
                    weights[m]= maxweight+1
        # now a list of tuples (weight,moduletuple) can easily be sorted:
        sort_list= sorted([(weights[m],m) for m in modules_set],
                          reverse= reverse)
        # created a list of moduletuples from the result:
        return [m for (_,m) in sort_list]
    def iter_modulenames(self):
        """return an iterator on module names."""
        return self.datadict().iterkeys()
    def iter_versions(self, modulename, archs, must_exist):
        """return an iterator on versionnames of a module.

        archs:
          This is the desired architecture. Only versions with that
          architecture are listed. If the architecture doesn't exist on at
          least one of the versions, a ValueError exception is raised.
          If arch is None, take any architectures.

        must_exist:
          If True if no versions are found raise a ValueError exception,
          otherwise just return.
        """
        found= False
        for versionname, versiondata in \
                self.datadict()[modulename].iteritems():
            if not self.__class__.check_arch(versiondata["archs"], archs):
                continue
            found= True
            yield versionname
        if must_exist and (not found):
            raise ValueError("All possible versions of module %s are "
                             "excluded because of the "
                             "set of archs" % \
                                     modulename)
    def sorted_moduleversions(self, modulename, archs, must_exist):
        """return an iterator on sorted versionnames of a module."""
        return sorted(self.iter_versions(modulename,
                                         archs, must_exist),
                      key= sumolib.utils.rev2key,
                      reverse= True)

    def patch_version(self, modulename, versionname, newversionname,
                      do_replace):
        """add a new version to the database by copying the old one.

        do_replace: if True, replace the old version with the new one
        """
        # pylint: disable=R0912
        #                          Too many branches
        moduledata= self.datadict().get(modulename)
        if moduledata is None:
            raise ValueError("error, module with name '%s' not found "
                             "in dependency database" % modulename)

        if moduledata.has_key(newversionname):
            raise ValueError("error, module %s: version %s already exists" % \
                    (modulename, newversionname))
        d= copy.deepcopy(self.datadict()[modulename][versionname])
        moduledata[newversionname]= d
        if do_replace:
            del moduledata[versionname]

    def clonemodule(self, old_modulename, modulename, versions):
        """Take all versions of old_modulename to create modulename.
        """
        old_moduledata= self.datadict()[old_modulename]
        if not versions:
            versions= list(self.iter_versions(old_modulename,
                                              archs= None, must_exist= True))
        if self.datadict().has_key(modulename):
            raise ValueError("error: module '%s' already exists" % \
                             modulename)
        m= self.datadict().setdefault(modulename,{})
        for version in versions:
            m[version]= copy.deepcopy(old_moduledata[version])

    def partial_copy_by_list(self, list_):
        """take items from the Dependencies object and create a new one.

        List must be a list of tuples in the form (modulename,versionname).

        This function copies modules whose versionname match *exactly* the
        given name, so "R1-3" and "1-3" are treated to be different.

        Note that the new Dependencies object only contains references of the
        data. This DOES NOT do a deep copy.

        """
        new= self.__class__()
        for modulename, versionname in list_:
            d= new.datadict().setdefault(modulename, {})
            # scan stable, testing and unstable versions:
            for version in self.iter_versions(modulename,
                                              None, must_exist= True):
                if not sumolib.ModuleSpec.Spec.compare_versions(version,\
                                                    versionname, "eq"):
                    continue
                d[version]= self.datadict()[modulename][version]
        return new
    def partial_copy_by_modulespecs(self, modulespecs):
        """take items from the Dependencies object and create a new one.

        modulespecs must be a sumolib.ModuleSpec.Specs object.

        Note that this function treats versions like "R1-3" and "1-3" to be
        different.

        If no versions are defined for a module, take all versions.
        If no archs are defined, take all archs.

        When no moduleversions are found, rause a ValueError exception.

        Note that the new Dependencies object only contains references of the
        data. This DOES NOT do a deep copy so you should NOT modify the
        result.
        """
        if not isinstance(modulespecs, sumolib.ModuleSpec.Specs):
            raise TypeError("wrong type: '%s'" % repr(modulespecs))
        new= self.__class__()
        for modulespec in modulespecs:
            modulename= modulespec.modulename
            archs= modulespec.archs
            d= new.datadict().setdefault(modulename, {})
            # scan stable, testing and unstable versions:
            for version in self.iter_versions(modulename,
                                              archs, must_exist= True):
                if not modulespec.test(version):
                    continue
                if not self.check_archs(modulename, version, archs):
                    continue
                d[version]= self.datadict()[modulename][version]
        return new
    def sets_dict(self, modulespecs):
        """create a dict of sets according to modulespecs.

        modulespecs must be a sumolib.ModuleSpec.Specs object.

        convert modulespecs to a sets dict:
        { modulename1 : set(version1,version2),
          modulename2 : set(version1,version2),
        }

        """
        if not isinstance(modulespecs, sumolib.ModuleSpec.Specs):
            raise TypeError("wrong type: '%s'" % repr(modulespecs))
        new= {}
        for modulespec in modulespecs:
            modulename= modulespec.modulename
            archs= modulespec.archs
            s= new.setdefault(modulename, set())
            found= False
            try:
                versions= list(self.iter_versions(modulename,
                                                  archs, must_exist= True))
            except KeyError, _:
                raise KeyError("error: module '%s' not found in "
                               "dependency database" % modulename)
            for version in versions:
                if not modulespec.test(version):
                    continue
                if not self.check_archs(modulename, version, archs):
                    continue
                found= True
                s.add(version)
            if not found:
                raise ValueError("error: no data found in dependency "
                                 "database for module specification '%s'" % \
                                 modulespec.to_string())
        return new
    def complete_sets_dict(self, sets_dict):
        """makes a sets_dict complete with respect to dependencies.

        A sets dict has this form:

        convert modulespecs to a sets dict:
        { modulename1 : set(version1,version2),
          modulename2 : set(version1,version2),
        }

        For each dependency that is missing, this program creates a new entry
        in the sets dict which contains all possible versions for the missing
        module.

        Returns a set of modulenames of added dependencies.
        """
        modules_added= set()
        modlist= sets_dict.keys()
        while modlist:
            new_modlist= []
            for modulename in modlist:
                for versionname in sets_dict[modulename]:
                    for dep_name in self.iter_dependencies(modulename,
                                                           versionname):
                        if not sets_dict.has_key(dep_name):
                            modules_added.add(dep_name)
                            sets_dict[dep_name]= \
                                      set(self.iter_versions(dep_name,\
                                                         archs=None,\
                                                         must_exist= True))
                            new_modlist.append(dep_name)
            modlist= new_modlist
        return modules_added
    def remove_missing_deps(self):
        """remove dependencies that are not part of the database."""
        modules= set(self.iter_modulenames())
        for modulename in self.iter_modulenames():
            for versionname in self.iter_versions(modulename,
                                                  None, False):
                if not self.dependencies_found(modulename, versionname):
                    continue
                deletions= []
                for dep_name in self.iter_dependencies(modulename,
                                                       versionname):
                    if dep_name not in modules:
                        deletions.append(dep_name)
                for dep_name in deletions:
                    try:
                        self.del_dependency(modulename, versionname,
                                            dep_name)
                    except ValueError, _:
                        pass

