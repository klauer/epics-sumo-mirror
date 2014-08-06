"""module specifications.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumo.[module]".
    sys.path.append("..")

import sumo.utils
import sumo.JSON
import sumo.Databases

# -----------------------------------------------
# modulespecification
# -----------------------------------------------

class Spec(object):
    """a class representing a single module specification."""
    def __init__(self, modulename, versionname, versionflag, archs):
        """initialize the object.

        Here are some examples:

        >>> Spec("ALARM","R3-2","eq",["A","B"])
        Spec('ALARM','R3-2','eq',['A', 'B'])
        >>> Spec("ALARM","R3-2","eq",None)
        Spec('ALARM','R3-2','eq',None)
        """
        self.modulename= modulename
        self.versionname= versionname
        self.versionflag= versionflag
        self.archs= archs
    def __repr__(self):
        """return repr string."""
        return "%s(%s,%s,%s,%s)" % (self.__class__.__name__,
                                 repr(self.modulename),
                                 repr(self.versionname),
                                 repr(self.versionflag),
                                 repr(self.archs))
    def no_version_spec(self):
        """returns True if there is no version spec."""
        return not self.versionname
    def is_exact_spec(self):
        """return if the spec is an exact version specification."""
        if not self.versionname:
            return False
        return self.versionflag=="eq"
    @classmethod
    def from_string(cls, spec, default_archs= None):
        """create modulespec from a string.

        A module specification has one of these forms:
          modulename
          modulename:version
          modulename::archs
          modulename:version:archs

        version may be:
          versionname        : exactly this version
          +versionname       : this version or newer
          -versionname       : this version or older

        archs may be:
          archspec{:archspec}

        archspec may be:
          +arch              : add this to the list of archs
          -arch              : remove this from the list of archs
           arch              : set exactly these archs (only of first arch has
                               this form)

        Here are some examples:

        >>> Spec.from_string("ALARM")
        Spec('ALARM',None,None,None)
        >>> Spec.from_string("ALARM:R3-2")
        Spec('ALARM','R3-2','eq',None)
        >>> Spec.from_string("ALARM:+R3-2")
        Spec('ALARM','R3-2','ge',None)
        >>> Spec.from_string("ALARM:-R3-2")
        Spec('ALARM','R3-2','le',None)

        >>> Spec.from_string("ALARM:R3-2:vxworks-ppc603")
        Spec('ALARM','R3-2','eq',set(['vxworks-ppc603']))
        >>> Spec.from_string("ALARM:R3-2:vxworks-ppc603:vxworks-mv162")
        Spec('ALARM','R3-2','eq',set(['vxworks-mv162', 'vxworks-ppc603']))

        >>> Spec.from_string("ALARM:R3-2:A:+B",["C"])
        Spec('ALARM','R3-2','eq',set(['A', 'B']))
        >>> Spec.from_string("ALARM:R3-2:+A:+B",["C"])
        Spec('ALARM','R3-2','eq',set(['A', 'C', 'B']))
        >>> Spec.from_string("ALARM:R3-2:+A:B",["C"])
        Spec('ALARM','R3-2','eq',set(['A', 'C', 'B']))
        """
        # pylint: disable=R0912
        #                          Too many branches
        mode= 0
        modulename= None
        versionname= None
        versionflag= None
        if default_archs is None:
            archs= set()
        else:
            archs= set(default_archs)
        for l in spec.split(":"):
            if mode==0:
                modulename= l
                mode+= 1
                continue
            if mode==1:
                if l!="":
                    if l[0]=="-":
                        versionname= l[1:]
                        versionflag= "le"
                    elif l[0]=="+":
                        versionname= l[1:]
                        versionflag= "ge"
                    else:
                        versionname= l
                        versionflag= "eq"
                mode+= 1
                continue
            if mode==2:
                if l[0]!="+" and l[0]!="-":
                    # overwrite default set of archs
                    archs= set([l])
                    mode=3
                    continue
                mode=3
            if mode==3:
                if l[0]=="+":
                    archs.add(l[1:])
                elif l[0]=="-":
                    archs.discard(l[1:])
                else:
                    archs.add(l)
                continue
        #print repr(modulename),repr(versionname),repr(versionflag),repr(archs)
        return cls(modulename,
                   versionname,
                   versionflag,
                   archs if archs else None)
    def to_string(self):
        """return a spec string.

        Here are some examples:

        >>> Spec("ALARM","R3-2","eq",["vxworks-ppc603"]).to_string()
        'ALARM:R3-2:vxworks-ppc603'
        >>> Spec("ALARM","R3-2","eq",["A","B"]).to_string()
        'ALARM:R3-2:A:B'
        >>> Spec("ALARM","R3-2","eq",None).to_string()
        'ALARM:R3-2'
        >>> Spec("ALARM","R3-2","ge",None).to_string()
        'ALARM:+R3-2'
        >>> Spec("ALARM","R3-2","le",None).to_string()
        'ALARM:-R3-2'
        >>> Spec("ALARM",None,None,None).to_string()
        'ALARM'
        >>> Spec("ALARM",None,None,["A","B"]).to_string()
        'ALARM::A:B'
        """
        elms= [self.modulename]
        if self.versionname:
            extra= ""
            if self.versionflag=="le":
                extra="-"
            elif self.versionflag=="ge":
                extra="+"
            elms.append("%s%s" % (extra, self.versionname))
        if self.archs:
            if not self.versionname:
                elms.append("")
            elms.extend(sorted(list(self.archs)))
        return ":".join(elms)
    @staticmethod
    def compare_versions(version1, version2, flag):
        """Test if a version matches another version."""
        if version1 is None:
            return True
        if version2 is None:
            return True
        if flag=="eq":
            return version1==version2
        k1= sumo.utils.rev2key(version1)
        k2= sumo.utils.rev2key(version2)
        #if self.versionflag=="=":
        #    return (k1==k2)
        if flag=="le":
            return k1>=k2
        if flag=="ge":
            return k1<=k2
        raise ValueError("unknown flag: '%s'" % repr(flag))

    def test(self, version):
        """Test if a version matches the spec.

        Here are some examples:
        >>> m= Spec.from_string("ALARM:R3-2")
        >>> m.test("R3-1")
        False
        >>> m.test("R3-2")
        True
        >>> m.test("R3-3")
        False

        >>> m= Spec.from_string("ALARM:-R3-2")
        >>> m.test("R3-1")
        True
        >>> m.test("R3-2")
        True
        >>> m.test("R3-3")
        False

        >>> m= Spec.from_string("ALARM:+R3-2")
        >>> m.test("R3-1")
        False
        >>> m.test("R3-2")
        True
        >>> m.test("R3-3")
        True
        """
        return Spec.compare_versions(self.versionname, version,
                                           self.versionflag)

class Specs(object):
    """A class representing a list of Spec objects."""
    # pylint: disable=R0903
    #         Too few public methods
    def __init__(self, speclist):
        """note: this DOES NOT a deep copy of the list.

        Here is an example:

        >>> def p(s):
        ...     for m in s:
        ...         print m

        >>> a=Spec('A','R2','eq',None)
        >>> b=Spec('B','R2','eq',None)
        >>> p(Specs((a,b)))
        Spec('A','R2','eq',None)
        Spec('B','R2','eq',None)
        """
        self.specs= speclist
    def __repr__(self):
        """return repr string."""
        return "%s(%s)" % (self.__class__.__name__,
                           ",".join([repr(s) for s in self.specs]))
    def __iter__(self):
        """the default iterator."""
        for m in self.specs:
            yield m
    @staticmethod
    def scan_special(st):
        """scan special in-line commands."""
        if not st:
            # empty string or None
            return None
        if st[0]!=":":
            return None
        return st[1:].split(":")
    @staticmethod
    def _from_strings(module_dict, idx, specs, builddb, default_archs):
        """internal function to scan specs.

        Note:
        module_dict maps a modulename to a pair (order-key,Spec-object).

        The order-key is used to give the list of modules the same sort order
        as they were found in the module specifications.
        """
        # pylint: disable=R0912
        #                          Too many branches
        for s in specs:
            special= Specs.scan_special(s)
            if special:
                # was special command
                if special[0]=="clear":
                    # clear module list so far
                    module_dict.clear()
                    continue
                if special[0]=="rm":
                    # remove single module
                    if len(special)<=1:
                        raise ValueError("argument to :rm: missing")
                    if module_dict.has_key(special[1]):
                        module_dict[special[1]][1]= None
                    continue
                if special[0]=="load":
                    if len(special)<=1:
                        raise ValueError("argument to :load: missing")
                    json_data= sumo.JSON.loadfile(special[1])
                    # pylint: disable=E1103
                    #         Instance of 'bool' has no 'get' member
                    json_specs= json_data.get("module")
                    if json_specs:
                        idx= Specs._from_strings(module_dict, idx,
                                                       json_specs,
                                                       builddb,
                                                       default_archs)
                    continue
                if special[0]=="build":
                    if len(special)<=1:
                        raise ValueError("argument to :build: missing")
                    if not builddb:
                        raise ValueError("error: builddb not specified")
                    if isinstance(builddb, str):
                        builddb= sumo.Databases.Builddb.from_json_file(
                                                                  builddb)
                    build_specs= builddb.module_specs(special[1])
                    idx= Specs._from_strings(module_dict, idx,
                                                   build_specs,
                                                   builddb,
                                                   default_archs)
                    continue

                raise ValueError("unexpected spec: %s" % s)
            m= Spec.from_string(s, default_archs)
            modulename= m.modulename
            if module_dict.has_key(modulename):
                module_dict[modulename][1]= m
                continue
            module_dict[modulename]= [idx, m]
            idx+= 1
        return idx

    @classmethod
    def from_strings(cls, specs, builddb_fn, default_archs= None):
        """scan a list of module specification strings.

        specs:  list of module specification strings
        builddb_fn: filename of builddb or the builddb itself,
                    only needed for :build:buildtag
        default_archs: list of default archs, may be None

        returns a new Specs object.

        Note that if a modulename is used twice, the later definition
        overwrites the first one. However, the module retains it's position in
        the internal list of modules.

        Here are some examples:

        >>> def p(s):
        ...     for m in s:
        ...         print m

        >>> p(Specs.from_strings(["A:R2","B:-R3","C:+R1:arch1"], None))
        Spec('A','R2','eq',None)
        Spec('B','R3','le',None)
        Spec('C','R1','ge',set(['arch1']))
        >>> p(Specs.from_strings(["A:R2","B:-R3","A:R3"], None))
        Spec('A','R3','eq',None)
        Spec('B','R3','le',None)
        >>> p(Specs.from_strings(["A:R2","B:-R3",":rm:A"], None))
        Spec('B','R3','le',None)
        >>> p(Specs.from_strings(["A:R2","B:-R3",":rm:A","A:R3"], None))
        Spec('A','R3','eq',None)
        Spec('B','R3','le',None)
        """
        module_dict= {}
        Specs._from_strings(module_dict, 0, specs, builddb_fn,
                                  default_archs)

        l= [modulespec for (_,modulespec) in sorted(module_dict.values()) \
                       if modulespec]
        return cls(l)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()