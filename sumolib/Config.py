"""Configuration file support.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os
import sys

import sumolib.JSON

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")


# -----------------------------------------------
# config file support
# -----------------------------------------------

class ConfigFile(object):
    """store options in a JSON file."""
    @classmethod
    def from_optionlist(cls, filename, optionlist):
        """Create object from optionlist."""
        d= dict( [(n,None) for n in optionlist])
        return cls(filename, d)
    def __init__(self, filename, dict_):
        """create from a dict."""
        self._filename= filename
        self.load_default= True
        self._dict= dict(dict_)
    def __repr__(self):
        """return repr string."""
        return "%s(%s, %s)" % (self.__class__.__name__,
                               repr(self._filename),
                               repr(self._dict))
    def __str__(self):
        """return string in human readable form."""
        lines= ["filename: %s\n" % self._filename,
                "dict:",
                str(self._dict)]
        return "\n".join(lines)

    def set(self, optionname, value):
        """set an option to an arbitrary value."""
        self._dict[optionname]= value
    def disable_default(self):
        """disable loading of the default file."""
        self.load_default= False
    def _merge(self, dict_):
        """merge known keys from dict_ with self."""
        for (key, val) in dict_.items():
            if not self._dict.has_key(key):
                continue # silently ignore unknown keys
            self._dict[key]= val
    def _load_file(self, filename):
        """load filename.

        Note that the special key "#include" means that another config file is
        included much as with the #include directive in C.
        """
        if not os.path.exists(filename):
            raise IOError("error: file \"%s\" doesn't exist" % filename)
        data= sumolib.JSON.loadfile(filename)
        # pylint: disable=E1103
        #                     Instance of 'bool' has no 'items' member
        includefiles= data.get("#include")
        if includefiles:
            for f in includefiles:
                self._load_file(f)
            del data["#include"]
        self._merge(data)
    def load(self, filenames):
        """first load self._filename, then filenames."""
        if self.load_default:
            lst= [self._filename]
        else:
            lst= []
        if filenames:
            lst.extend(filenames)
        for filename in lst:
            self._load_file(filename)
    def save(self, filename, keys):
        """dump in json format"""
        # do not include "None" values:
        dump= {}
        if not keys:
            keys= self._dict.keys()
        for k in keys:
            # we do not distinguish here between items that don't exist
            # and items that have value "None":
            v= self._dict.get(k)
            if v is None:
                continue
            dump[k]= v
        if filename=="-":
            sumolib.JSON.dump(dump)
            return
        if filename=="DEFAULT":
            filename= self._filename
        sumolib.JSON.dump_file(filename, dump)

    def merge_options(self, option_obj, list_merge_opts):
        """create from an option object.

        Merge Config object with command line options and
        command line options with Config object.

        All options that are part of the list <list_merge_opts> must be lists.
        For these options the lists are *merged*, meaning that the new list is
        the sum of both lists. It is ensured that for all elements the string
        up to the first colon ":" is unique in the list (in order to be usable
        for module specs in the form "module:version").
        """
        # pylint: disable=R0912
        #                          Too many branches
        def list2dict(l):
            """convert ["k1:v1","k2:v2"...] to {"k1":"v1","k2":"v2"...}.
            """
            return dict([s.split(":",1) for s in l])
        def dict2list(d):
            """convert {"k1":"v1","k2":"v2"...} to ["k1:v1","k2:v2"...].
            """
            return sorted([":".join((k,v)) for (k,v) in d.items()])
        def list_merge(a,b,name):
            """merge two lists."""
            if not isinstance(a, list):
                raise TypeError("error: %s from config file(s) is not "
                                "a list" % name)
            if not isinstance(b, list):
                raise TypeError("error: %s from command line options "
                                "is not a list" % name)
            d= list2dict(a)
            d.update(list2dict(b))
            return dict2list(d)

        if list_merge_opts is None:
            list_merge_opts_set= set()
        else:
            for opt in list_merge_opts:
                if not hasattr(option_obj, opt):
                    raise ValueError(
                        "error: '%s' is not a known option" % opt)
            list_merge_opts_set= set(list_merge_opts)
        # copy from option_obj to self:
        for opt in self._dict.keys():
            if not hasattr(option_obj, opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            val= getattr(option_obj, opt)
            if val is not None:
                existing= self._dict.get(opt)
                if existing is None:
                    self._dict[opt]= val
                else:
                    if opt not in list_merge_opts_set:
                        self._dict[opt]= val
                    else:
                        self._dict[opt]= list_merge(existing, val, opt)

        # copy from self to option_obj:
        for (opt, val) in self._dict.items():
            if not hasattr(option_obj, opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            if val is not None:
                setattr(option_obj, opt, val)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
