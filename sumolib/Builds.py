"""Database file handling.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import sumolib.ModuleSpec
import sumolib.JSON

__version__="2.3.1" #VERSION#

assert __version__==sumolib.ModuleSpec.__version__
assert __version__==sumolib.JSON.__version__

# -----------------------------------------------
# warnings
# -----------------------------------------------

def warn(text):
    """print a warning to the console."""
    sys.stderr.write(text+"\n")

# -----------------------------------------------
# class definitions
# -----------------------------------------------

class DB(sumolib.JSON.Container):
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
        raise ValueError("error: builddb data is invalid %s" % msg)
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
        super(DB, self).__init__(dict_)
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
        data= sumolib.JSON.loadfile(filename)
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
    def is_unstable(self, build_tag):
        """returns True if the build is marked testing or stable.
        """
        d= self.datadict()
        s= d[build_tag]["state"]
        return s=="unstable"
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
        if not isinstance(modulespecs, sumolib.ModuleSpec.Specs):
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
        sumolib.ModuleSpec.Spec.from_string().
        """
        lst= []
        build_dict= self.modules(build_tag)
        for modulename in sorted(build_dict.keys()):
            versionname= build_dict[modulename]
            m= sumolib.ModuleSpec.Spec(modulename, versionname,
                                     "eq", default_archs)
            lst.append(m.to_string())
        return lst

class BuildCache(sumolib.JSON.Container):
    """Detailed dependency information.

    Taken from sumo-scan and from the build database.

    { "modulename": { "versionname": { "depmodule" :
                                       {
                                         "depvers1": state,
                                         "depvers2": state
                                       }
                                     }
                    }
    }
    """
    def __init__(self, dict_= None):
        """create the object."""
        super(BuildCache, self).__init__(dict_)
    def add_dependency(self, modulename, versionname,
                       dep_name, dep_version, state):
        """add a single dependency with a state."""
        # pylint: disable=R0913
        #                          Too many arguments
        d= self.datadict()
        versiondict   = d.setdefault(modulename, {})
        depmoduledict = versiondict.setdefault(versionname, {})
        depversiondict= depmoduledict.setdefault(dep_name, {})
        depversiondict[dep_version]= state
    def update_from_builddb(self, builddb, db):
        """update data from a builddb.
        """
        # pylint: disable=R0914
        #                          Too many local variables
        d= self.datadict()
        for buildtag in builddb.iter_builds():
            state= builddb.state(buildtag)
            # skip builds marked "unstable":
            if builddb.is_unstable(buildtag):
                continue
            # set per build, contains (modulename,versionname)
            build_dict= {}
            for modulename, versionname in builddb.iter_modules(buildtag):
                build_dict[modulename]= versionname
            for (modulename, versionname) in build_dict.items():
                versiondict   = d.setdefault(modulename, {})
                depmoduledict = versiondict.setdefault(versionname, {})
                try:
                    dep_names= list(db.iter_dependencies(modulename,
                                                         versionname))
                except KeyError, _:
                    warn("WARNING: build '%s', module '%s:%s' not "
                         "in dependency db!" % \
                         (buildtag,modulename,versionname))
                    continue
                for dep_name in dep_names:
                    v= build_dict.get(dep_name)
                    if v is not None:
                        depversiondict= depmoduledict.setdefault(dep_name, {})
                        depversiondict[v]= state

    def was_built(self, modulename, versionname):
        """return True when the module was built sometime.
        """
        d= self.datadict()
        versiondict   = d.get(modulename)
        if not versiondict:
            return False
        return versiondict.has_key(versionname)
    def relation(self, modulename, versionname, dep_name, dep_version):
        """return the relation between two modules.

        None: unrelated
        <state>: built together in a build with state <state>.
        """
        d= self.datadict()
        versiondict   = d.get(modulename)
        if not versiondict:
            return None
        depmoduledict = versiondict.get(versionname)
        if not depmoduledict:
            return None
        depversiondict= depmoduledict.get(dep_name)
        if not depversiondict:
            return None
        return depversiondict.get(dep_version)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
