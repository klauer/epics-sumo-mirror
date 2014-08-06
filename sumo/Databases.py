"""Database file handling.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys
import copy
import sumo.ModuleSpec

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumo.[module]".
    sys.path.append("..")

import sumo.JSON

import sumo.utils

class Dependencies(sumo.JSON.Container):
    """the dependency database."""
    # pylint: disable=R0904
    #                          Too many public methods
    # pylint: disable=R0913
    #                          Too many arguments
    states_list= ["stable", "testing", "unstable"]
    states_dict= dict(zip(states_list,range(len(states_list))))
    SUM_MIN= 0
    SUM_MAX= 1
    SUM_FIRST= 2
    @classmethod
    def check_state(cls, state):
        """checks if a state is allowed."""
        if not cls.states_dict.has_key(state):
            raise ValueError("unknown state: %s" % repr(state))
    @classmethod
    def _sum_state(cls, mode, state1, state2):
        """return a sum state of a list of states.

        known modes:
          SUM_MIN: minimize state, "stable"<"testing"<"unstable"
          SUM_MAX: maximize state, "stable"<"testing"<"unstable"
          SUM_FIRST: just take state1
        """
        if mode==cls.SUM_FIRST:
            if not cls.states_dict.has_key(state1):
                raise KeyError("unknown state: %s" % repr(state1))
            return state1
        if mode==cls.SUM_MIN:
            i= min(cls.states_dict[state1], cls.states_dict[state2])
        elif mode==cls.SUM_MAX:
            i= max(cls.states_dict[state1], cls.states_dict[state2])
        else:
            raise ValueError("unknown mode: %s" % repr(mode))
        return cls.states_list[i]
    @classmethod
    def _allowed_states(cls, max_state):
        """generate a list of allowed states from a maximum state.
        """
        idx= cls.states_dict.get(max_state)
        if idx is None:
            raise ValueError("invalid max_state: %s" % max_state)
        return set( [x for x in cls.states_list if cls.states_dict[x]<=idx])
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
    @classmethod
    def _dependency_merge(cls, src_deps, dest_deps,
                          constant_src_state,
                          state_sum_mode):
        """intelligent merge of dependency dicts.
        """
        for modulename, src_dep_dict in src_deps.items():
            dest_dep_dict= dest_deps.setdefault(modulename, {})
            for src_ver, src_state in src_dep_dict.items():
                if constant_src_state is not None:
                    src_state= constant_src_state
                dest_state= dest_dep_dict.get(src_ver)
                if dest_state is None:
                    dest_dep_dict[src_ver]= src_state
                    continue
                dest_dep_dict[src_ver]= \
                        cls._sum_state(state_sum_mode,
                                       src_state, dest_state)
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
            src= version.get("source")
            if not src:
                break
            return
        raise ValueError("Error: Dependency data is invalid %s" % msg)
    def __init__(self, dict_= None):
        """create the object."""
        super(Dependencies, self).__init__(dict_)
    def merge(self, other,
              constant_src_state,
              state_sum_mode):
        """merge another Dependencies object to self.

        parameters:
            self  - the object itself
            other - the other Dependencies object
            constant_src_state -
                    take this as exting state in "self" instead of the state
                    that is actually stored there.
            state_sum_mode -
                    determine the mode states are combinde. Must be
                    Dependencies.SUM_FIRST, Dependencies.SUM_MIN or
                    Dependencies.SUM_MAX.
        """
        # pylint: disable=R0912
        #                          Too many branches
        for modulename in other.iter_modulenames():
            m= self.datadict().setdefault(modulename,{})
            # iterate on stable, testing and unstable versions:
            for versionname in other.iter_versions(modulename, "unstable",
                                                   None, False):
                vdict = m.setdefault(versionname,{})
                vdict2= other.datadict()[modulename][versionname]
                for dictname, dictval in vdict2.items():
                    if dictname=="state":
                        # pylint: disable=W0212
                        #         Access to a protected member
                        if constant_src_state is not None:
                            src_state= constant_src_state
                        else:
                            src_state= vdict2[dictname]
                        if vdict.has_key(dictname):
                            vdict[dictname]= self.__class__._sum_state(
                                    state_sum_mode,
                                    src_state,
                                    vdict[dictname])
                        else:
                            vdict[dictname]= src_state
                        # pylint: enable=W0212
                        continue
                    if dictname=="archs":
                        try:
                            sumo.utils.dict_update(
                                        vdict.setdefault(dictname,{}),
                                        dictval)
                        except ValueError, e:
                            raise ValueError(
                              "module %s version %s archs: %s" % \
                              (modulename, versionname, str(e)))
                        continue
                    if dictname=="weight":
                        # take the weight from the new dict if present
                        vdict[dictname]= dictval
                        continue
                    if dictname=="aliases":
                        try:
                            sumo.utils.dict_update(
                                        vdict.setdefault(dictname,{}),
                                        dictval)
                        except ValueError, e:
                            raise ValueError(
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
                        # pylint: disable=W0212
                        #         Access to a protected member
                        self.__class__._dependency_merge(
                                dictval,
                                vdict.setdefault(dictname,{}),
                                constant_src_state,
                                state_sum_mode)
                        # pylint: enable=W0212
                        continue
                    raise AssertionError("unexpected dictname %s" % dictname)
    def import_module(self, other, module_name, versionname):
        """copy the module data from another Dependencies object.

        This does a deepcopy of the data.
        """
        m= self.datadict().setdefault(module_name,{})
        m[versionname]= copy.deepcopy(
                            other.datadict()[module_name][versionname])
    def set_source(self, module_name, versionname, new):
        """add a module with source spec, state and archs.

        [new] must be a dictionary as it is used in key "source" in
        Dependencies objects. Examples:
            {'path': 'ab'}
            {'darcs': {'url': 'abc'}}
            {'darcs': {'url': 'abc', 'tag': 'R1-2'}}

        The dictionary has a single key that is called the source type that
        maps to property dictionary.

        The property dictionary in [new] may contain the special wildcard
        string "*".

        If the source type for the module and the source type in [new] are
        different, this function just sets the module source to [new].

        If the source type for the module and the source type in [new] are the
        same, the property string is updated from the property string in [new].
        Where the property string in [new] contains the string "*", the
        property of the module remains unchanged.
        """
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        source= version.get("source")
        if not source:
            version["source"]= new
            return
        (source_type,source_dict)= sumo.utils.single_key_item(source)
        (new_type,new_dict)= sumo.utils.single_key_item(new)
        if source_type==new_type:
            for (k,v) in new_dict.items():
                if v=="*":
                    n= source_dict.get(k)
                    if n:
                        new_dict[k]= n
        version["source"]= new
    def set_source_arch_state(self, module_name, versionname, archs, state,
                              repo_dict):
        """add a module with source spec, state and archs."""
        if not self.__class__.states_dict.has_key(state):
            raise ValueError("invalid state: %s" % state)
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        if not version.has_key("state"):
            version["state"]= state
        arch_dict= version.setdefault("archs", {})
        for arch in archs:
            arch_dict[arch]= True
        version["source"]= repo_dict
    def add_dependency(self, modulename, versionname,
                       dep_modulename, dep_versionname, state):
        """add dependency for a module:version.
        """
        self.__class__.check_state(state)
        m_dict= self.datadict()[modulename]
        dep_dict= m_dict[versionname].setdefault("dependencies",{})
        dep_module_dict= dep_dict.setdefault(dep_modulename, {})
        if dep_module_dict.has_key(dep_versionname):
            raise ValueError("module '%s:%s' already has dependency "
                             "'%s:%s'" % \
                             (modulename, versionname,
                              dep_modulename, dep_versionname))
        dep_module_dict[dep_versionname]= state
    def del_dependency(self, modulename, versionname,
                       dep_modulename, dep_versionname):
        """delete dependency for a module:version if it exists.
        """
        m_dict= self.datadict()[modulename]
        dep_dict= m_dict[versionname].get("dependencies")
        if dep_dict is None:
            raise ValueError("Error, %s:%s has no dependencies" % \
                             (modulename, versionname))
        dep_module_dict= dep_dict.get(dep_modulename)
        if dep_module_dict is None:
            raise ValueError("Error, %s:%s doesn't depend on %s" % \
                             (modulename, versionname, dep_modulename))
        if not dep_module_dict.has_key(dep_versionname):
            raise ValueError("Error, %s:%s doesn't depend on %s:%s" % \
                             (modulename, versionname,
                              dep_modulename, dep_versionname))
        del dep_module_dict[dep_versionname]
        if not dep_module_dict:
            # dict is now empty, delete the whole entry in "dependencies":
            del dep_dict[dep_modulename]
        if not dep_dict:
            # "dependencies" is now empty, remove it:
            del m_dict[versionname]["dependencies"]
    def check(self):
        """do a consistency check on the db."""
        msg= []
        for modulename in self.iter_modulenames():
            for versionname in self.iter_versions(modulename, "unstable",
                                                  None, True):
                archs= self.get_archs(modulename, versionname).keys()
                if len(archs)==0:
                    msg.append("%s:%s: no target architectures" % \
                               (modulename, versionname))
                for dep_modulename in self.iter_dependencies(modulename,
                                                             versionname):
                    for dep_version in self.sorted_dependency_versions(
                            modulename, versionname, dep_modulename,
                            "unstable", None):
                        try:
                            self.assert_module(dep_modulename, dep_version)
                        except KeyError, e:
                            msg.append("%s:%s: dependencies: %s" % \
                                    (modulename, versionname, str(e)))
        return msg
    def search_modules(self, rx_object, max_state, archs):
        """search module names and source URLS for a regexp.

        Returns a list of tuples (modulename, versionname).
        """
        results= []
        for modulename in self.iter_modulenames():
            if rx_object.search(modulename):
                for versionname in self.iter_versions(modulename,
                                                      max_state,
                                                      archs, False):
                    results.append((modulename, versionname))
                continue
            for versionname in self.iter_versions(modulename,
                                                  max_state,
                                                  archs, False):
                url= self.module_source_url(modulename, versionname)
                if rx_object.search(url):
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
        return self.__class__.check_arch(
                   self.get_archs(modulename, versionname), archs)
    def add_alias(self, modulename, versionname,
                  alias_name, real_name):
        """add an alias for modulename:versionname."""
        m_dict= self.datadict()[modulename]
        alias_dict= m_dict[versionname].setdefault("aliases",{})
        if alias_dict.has_key(real_name):
            if alias_dict[real_name]==alias_name:
                return
            raise ValueError(
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
        """
        d= self.datadict().get(modulename)
        if d is None:
            raise KeyError("no data for module %s" % modulename)
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
        """return a tuple (type,dict) for the module source."""
        l= self.datadict()[modulename][versionname]["source"]
        return sumo.utils.single_key_item(l)
    def module_source_url(self, modulename, versionname):
        """return the source url or path for a module."""
        (tp,val)= self.module_source_dict(modulename, versionname)
        if tp=="path":
            return val
        elif tp=="darcs":
            return val["url"]
        else:
            raise AssertionError("unexpected source tag %s at %s:%s" % \
                    (tp, modulename, versionname))
    def iter_dependencies(self, modulename, versionname):
        """return an iterator on dependency modulenames of a module."""
        d= self.datadict()[modulename][versionname]
        deps= d.get("dependencies")
        if deps is None:
            return iter([])
        return deps.iterkeys()
    def depends_on(self, modulename, versionname,
                   dependencyname, dependencyversion):
        """returns True if given dependency is found.
        """
        d= self.datadict()[modulename][versionname]
        deps= d.get("dependencies")
        if deps is None:
            return False
        dep_dict= deps.get(dependencyname)
        if dep_dict is None:
            return False
        return dep_dict.has_key(dependencyversion)
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
        dependencies= {}
        weights= {}
        i=0
        for m in moduleversions:
            weights[m]= i
            i+= 1

        # collect all direct dependencies:
        modules_set= set(moduleversions)
        for (modulename, versionname) in modules_set:
            s= set()
            dependencies[(modulename, versionname)]= s
            for dep_name in self.iter_dependencies(modulename, versionname):
                for dep_version in self.iter_dependency_versions(modulename,
                                                                 versionname,
                                                                 dep_name,
                                                                 "unstable",
                                                                 None):
                    if not (dep_name,dep_version) in modules_set:
                        continue
                    s.add((dep_name,dep_version))

        # add all indirect dependencies:
        changes= True
        while changes:
            changes= False
            for m in modules_set:
                deps= dependencies[m]
                for dep_m in list(deps):
                    depdeps= dependencies[dep_m]
                    for depdeps_m in depdeps:
                        if depdeps_m not in deps:
                            changes= True
                            deps.add(depdeps_m)

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

    def iter_dependency_versions(self, modulename, versionname,
                                 dependencyname, max_state,
                                 archs):
        """return an iterator on dependency versions.

        max_state :
          This is the maximum allowed state:
            "stable"  : return just stable
            "testing" : return stable and testing
            "unstable": return stable, testing and unstable

        archs:
          This is the desired architecture. Only dependencies with that
          architecture are listed. If the architecture doesn't exist on at
          least one of the dependencies or the module itself, a ValueError
          exception is raised.
          If arch is None do not check architectures.
        """
        # pylint: disable=W0212
        #                          Access to a protected member of a
        #                          client class
        _states= self.__class__._allowed_states(max_state)
        # pylint: enable=W0212
        d= self.datadict()[modulename][versionname]
        if archs is not None:
            if not self.__class__.check_arch(d["archs"], archs):
                raise ValueError("archs %s not supported in %s:%s" % \
                                 (repr(archs),modulename, versionname))
        deps= d.get("dependencies")
        if deps is None:
            raise StopIteration
        dep_dict= deps.get(dependencyname,{})
        if dep_dict is None:
            raise StopIteration
        found= False
        for (dep_version, dep_state) in dep_dict.iteritems():
            if dep_state not in _states:
                continue
            if archs is not None:
                if not self.check_archs(dependencyname, dep_version, archs):
                    #sys.stderr.write("check_archs(%s,%s,%s)==FALSE\n" % \
                    #        (repr(dependencyname),repr(dep_version),
                    #         repr(archs)))
                    continue
            found= True
            yield dep_version
        if not found:
            raise ValueError("all dependencies excluded because of state "
                             "or arch in module %s:%s. With given state "
                             "and archs the module cannot be built." % \
                                     (modulename, versionname))
    def sorted_dependency_versions(self, modulename, versionname,
                                   dependencyname, max_state, archs):
        """return sorted dependency versions.

        max_state is the maximum allowed state:
          "stable"  : return just stable
          "testing" : return stable and testing
          "unstable": return stable, testing and unstable

        archs:
          This is the desired architecture. Only dependencies with that
          architecture are listed. If the architecture doesn't exist on at
          least one of the dependencies or the module itself, a ValueError
          exception is raised.
          If arch is None do not check architectures.
        """
        dep_list= list(self.iter_dependency_versions(modulename, versionname,
                                                     dependencyname,
                                                     max_state, archs))
        dep_list.sort(key= sumo.utils.rev2key, reverse= True)
        return dep_list
    def iter_modulenames(self):
        """return an iterator on module names."""
        return self.datadict().iterkeys()
    def iter_versions(self, modulename, max_state, archs, must_exist):
        """return an iterator on versionnames of a module.

        max_state:
          This is the maximum allowed state:
          "stable"  : return just stable
          "testing" : return stable and testing
          "unstable": return stable, testing and unstable

        archs:
          This is the desired architecture. Only versions with that
          architecture are listed. If the architecture doesn't exist on at
          least one of the versions, a ValueError exception is raised.
          If arch is None, take any architectures.

        must_exist:
          If True if no versions are found raise a ValueError exception,
          otherwise just return.
        """
        # pylint: disable=W0212
        #                          Access to a protected member of a
        #                          client class
        _states= self.__class__._allowed_states(max_state)
        # pylint: enable=W0212
        found= False
        for versionname, versiondata in \
                self.datadict()[modulename].iteritems():
            if versiondata["state"] not in _states:
                continue
            if not self.__class__.check_arch(versiondata["archs"], archs):
                continue
            found= True
            yield versionname
        if must_exist and (not found):
            raise ValueError("All possible versions of module %s are "
                             "excluded because of the required state or "
                             "set of archs" % \
                                     modulename)
    def sorted_moduleversions(self, modulename, max_state, archs, must_exist):
        """return an iterator on sorted versionnames of a module."""
        return sorted(self.iter_versions(modulename, max_state,
                                         archs, must_exist),
                      key= sumo.utils.rev2key,
                      reverse= True)

    def patch_version(self, modulename, versionname, newversionname,
                      do_replace):
        """add a new version to the database by copying the old one.

        do_replace: if True, replace the old version with the new one
        Note: the state of the new version is always set to unstable.
        """
        # pylint: disable=R0912
        #                          Too many branches
        moduledata= self.datadict()[modulename]
        if moduledata.has_key(newversionname):
            raise ValueError("module %s: version %s already exists" % \
                    (modulename, newversionname))
        d= copy.deepcopy(self.datadict()[modulename][versionname])
        d["state"]= "unstable"
        moduledata[newversionname]= d
        if do_replace:
            del moduledata[versionname]
        # now scan all the references to modulename:versionname :
        for l_modulename in self.iter_modulenames():
            # scan stable, testing and unstable versions:
            for l_versionname in self.iter_versions(l_modulename,
                                                    "unstable", None, False):
                vd= self.datadict()[l_modulename][l_versionname]
                dep_dict= vd.get("dependencies")
                if dep_dict is None:
                    continue
                dep_module_dict= dep_dict.get(modulename)
                if dep_module_dict is None:
                    continue
                if not dep_module_dict.has_key(versionname):
                    continue
                if do_replace:
                    del dep_module_dict[versionname]
                # set the new dependency always to "unstable":
                dep_module_dict[newversionname]= "unstable"

    def clonemodule(self, old_modulename, modulename, versions):
        """Take all versions of old_modulename to create modulename.
        """
        old_moduledata= self.datadict()[old_modulename]
        if not versions:
            versions= list(self.iter_versions(old_modulename,
                                              max_state= "unstable",
                                              archs= None, must_exist= True))
        if self.datadict().has_key(modulename):
            raise ValueError("Error, module '%s' already exists" % \
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
            for version in self.iter_versions(modulename, "unstable",
                                              None, must_exist= True):
                if not sumo.ModuleSpec.Spec.compare_versions(version,
                                                    versionname, "eq"):
                    continue
                d[version]= self.datadict()[modulename][version]
        return new
    def partial_copy_by_modulespecs(self, modulespecs):
        """take items from the Dependencies object and create a new one.

        modulespecs must be a sumo.ModuleSpec.Specs object.

        Note that this function treats versions like "R1-3" and "1-3" to be
        different.

        If no versions are defined for a module, take all versions.
        If no archs are defined, take all archs.

        When no moduleversions are found, rause a ValueError exception.

        Note that the new Dependencies object only contains references of the
        data. This DOES NOT do a deep copy so you should NOT modify the
        result.
        """
        if not isinstance(modulespecs, sumo.ModuleSpec.Specs):
            raise TypeError("wrong type: '%s'" % repr(modulespecs))
        new= self.__class__()
        for modulespec in modulespecs:
            modulename= modulespec.modulename
            archs= modulespec.archs
            d= new.datadict().setdefault(modulename, {})
            # scan stable, testing and unstable versions:
            for version in self.iter_versions(modulename, "unstable",
                                              archs, must_exist= True):
                if not modulespec.test(version):
                    continue
                if not self.check_archs(modulename, version, archs):
                    continue
                d[version]= self.datadict()[modulename][version]
        return new
    def remove_missing_deps(self):
        """remove dependencies that are not part of the database."""
        modules= set()
        for modulename in self.iter_modulenames():
            for versionname in self.iter_versions(modulename, "unstable",
                                                  None, False):
                modules.add((modulename, versionname))
        for modulename in self.iter_modulenames():
            for versionname in self.iter_versions(modulename, "unstable",
                                                  None, False):
                if not self.dependencies_found(modulename, versionname):
                    continue
                deletions= []
                for dep_name in self.iter_dependencies(modulename,
                                                       versionname):
                    for dep_ver in self.iter_dependency_versions(modulename,
                                                                 versionname,
                                                                 dep_name,
                                                                 "unstable",
                                                                 None):
                        if not (dep_name,dep_ver) in modules:
                            deletions.append((dep_name, dep_ver))
                for (dep_name, dep_ver) in deletions:
                    try:
                        self.del_dependency(modulename, versionname,
                                            dep_name, dep_ver)
                    except ValueError, _:
                        pass

class Builddb(sumo.JSON.Container):
    """the buildtree database."""
    # pylint: disable=R0904
    #                          Too many public methods
    states= set(("stable","testing","unstable"))
    @classmethod
    def check_state(cls, state):
        """checks if a state is allowed."""
        if not state in cls.states:
            raise ValueError("unknown state: %s" % repr(state))
    def selfcheck(self, msg):
        """raise exception if obj doesn't look like a builddb."""
        def _somevalue(d):
            """return kind of arbitrary value of a dict."""
            keys= d.keys()
            key= keys[len(keys)/2]
            return d[key]
        while True:
            d= self.datadict()
            if not isinstance(d, dict):
                break
            if not d:
                # empty directory
                # this may be OK:
                return
            build= _somevalue(d)
            if not isinstance(build, dict):
                break
            modules= build.get("modules")
            if not modules:
                break
            if not isinstance(modules, dict):
                break
            module= _somevalue(modules)
            if not (isinstance(module, str) or isinstance(module, unicode)):
                break
            return
        raise ValueError("Error: Builddb data is invalid %s" % msg)
    def generate_buildtag(self, buildtag_stem):
        """generate a new buildtag.

        A new buildtag in the form "STEM-nnn" is generated.
        """
        # determine which number to append:
        no= None
        buildtag_stem= buildtag_stem + "-"
        for b in self.iter_builds():
            if b.startswith(buildtag_stem):
                b= b.replace(buildtag_stem,"")
                try:
                    n= int(b)
                except ValueError, _:
                    continue
                if n>no:
                    no= n
        if no is None:
            no= 0
        no+= 1
        return "%s%03d" % (buildtag_stem, no)
    @staticmethod
    def is_generated_buildtag(buildtag):
        """return True of the buildtag was generated."""
        return buildtag.startswith("AUTO-")
    def __init__(self, dict_= None):
        """create the object."""
        super(Builddb, self).__init__(dict_)
    def is_empty(self):
        """shows of the object is empty."""
        return not bool(self.datadict())
    def add(self, other):
        """add data from a dict."""
        d= self.datadict()
        for key in ["modules", "linked"]:
            d[key].update(other[key])
    def add_json_file(self, filename):
        """add data from a JSON file."""
        data= sumo.JSON.loadfile(filename)
        self.add(data)
    def delete(self, build_tag):
        """delete a build."""
        d= self.datadict()
        del d[build_tag]
    def has_build_tag(self, build_tag):
        """returns if build_tag is contained."""
        return self.datadict().has_key(build_tag)
    def new_build(self, build_tag, state):
        """create a new build with the given state.
        """
        # may raise ValueError:
        self.__class__.check_state(state)
        d= self.datadict()
        if d.has_key(build_tag):
            raise ValueError("cannot create, build %s already exists" % \
                               build_tag)
        d[build_tag]= { "state": state }
    def is_stable(self, build_tag):
        """returns True if the build is marked stable.
        """
        d= self.datadict()
        return d[build_tag]["state"] == "stable"
    def is_testing_or_stable(self, build_tag):
        """returns True if the build is marked testing or stable.
        """
        d= self.datadict()
        s= d[build_tag]["state"]
        return (s=="testing") or (s=="stable")
    def state(self, build_tag):
        """return the state of the build."""
        d= self.datadict()
        return d[build_tag]["state"]
    def change_state(self, build_tag, new_state):
        """sets the state to a new value."""
        # may raise ValueError:
        self.__class__.check_state(new_state)
        d= self.datadict()
        d[build_tag]["state"]= new_state
    def is_fully_linked(self, build_tag):
        """returns True if the build consists *only* of links."""
        build_= self.datadict()[build_tag]
        modules_= build_["modules"]
        linked_ = build_.get("linked")
        if not linked_:
            return False
        if len(modules_)>len(linked_):
            return False
        return True
    def add_build(self, other, build_tag):
        """add build data from another Builddb to this one.

        Note: this does NOT do a deep copy, it copies just references.
        """
        d= self.datadict()
        if d.has_key(build_tag):
            raise ValueError("cannot add, build %s already exists" % build_tag)
        d[build_tag]= other.datadict()[build_tag]
    def add_module(self, build_tag,
                   module_build_tag,
                   modulename, versionname):
        """add a module definition."""
        build_= self.datadict().setdefault(build_tag, {})
        modules_= build_.setdefault("modules", {})
        modules_[modulename]= versionname
        if build_tag!= module_build_tag:
            linked_ = build_.setdefault("linked", {})
            linked_[modulename]= module_build_tag
    def has_module(self, build_tag, modulename):
        """returns if the module is contained here."""
        build_= self.datadict()[build_tag]
        module_dict= build_["modules"]
        return module_dict.has_key(modulename)
    def module_version(self, build_tag, modulename):
        """returns the version of the module or None."""
        build_= self.datadict()[build_tag]
        module_dict= build_["modules"]
        return module_dict.get(modulename)

    def module_link(self, build_tag,
                    modulename):
        """return linked build_tag if the module is linked or None."""
        build_= self.datadict()[build_tag]
        linked_ = build_.get("linked")
        if linked_ is None:
            return
        return linked_.get(modulename)
    def is_linked_to(self, build_tag, other_build_tag):
        """returns True if there are links to other_build_tag."""
        build_= self.datadict()[build_tag]
        linked_ = build_.get("linked")
        if linked_ is None:
            return False
        for v in linked_.values():
            if v== other_build_tag:
                return True
        return False
    def filter_by_modulespecs(self, modulespecs, db):
        """return a new Builddb that satisfies the given list of specs.

        Note that this function treats versions like "R1-3" and "1-3" to be
        different.
        """
        if not isinstance(modulespecs, sumo.ModuleSpec.Specs):
            raise TypeError("wrong type: '%s'" % repr(modulespecs))
        new= self.__class__()
        for build_tag in self.iter_builds():
            found= True
            m= self.modules(build_tag)
            for modulespec in modulespecs:
                modulename= modulespec.modulename
                v= m.get(modulename)
                if v is None:
                    found= False
                    break
                if not modulespec.test(v):
                    found= False
                    break
                if not db.check_archs(modulename, v, modulespec.archs):
                    found= False
                    break
            if found:
                new.add_build(self, build_tag)
        return new
    def iter_builds(self):
        """return a build iterator.
        """
        for t in sorted(self.datadict().keys()):
            yield t
    def iter_modules(self, build_tag):
        """return an iterator on the modules."""
        build_= self.datadict()[build_tag]
        module_dict= build_["modules"]
        for module in sorted(module_dict.keys()):
            yield (module, module_dict[module])
    def modules(self, build_tag):
        """return all modules of a build.

        The returned structure is a dictionary mapping modulenames to
        versionnames.
        """
        build_ = self.datadict()[build_tag]
        return build_["modules"]
    def module_specs(self, build_tag, default_archs=None):
        """return the modules of a build in form module spec strings.

        This function returns a list of strings that ccan be parsed by
        sumo.ModuleSpec.Spec.from_string().
        """
        lst= []
        build_dict= self.modules(build_tag)
        for modulename in sorted(build_dict.keys()):
            versionname= build_dict[modulename]
            m= sumo.ModuleSpec.Spec(modulename, versionname,
                                     "eq", default_archs)
            lst.append(m.to_string())
        return lst


def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
