"""Configuration file support.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os
import sys
import platform

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import sumolib.JSON

__version__="2.2.2" #VERSION#

assert __version__==sumolib.JSON.__version__

# -----------------------------------------------
# config file support
# -----------------------------------------------

class ConfigFile(object):
    """store options in a JSON file."""
    @staticmethod
    def paths_from_env(varname):
        """read configuration paths from environment variable."""
        val= os.environ.get(varname)
        if not val:
            return
        # allow ":" and ";" as separators:
        if platform.system()=="Windows":
            sep= ";"
        else:
            sep= ":"
        return val.split(sep)
    @classmethod
    def from_optionlist(cls, filename, env_name, optionlist):
        """Create object from optionlist."""
        d= dict( [(n,None) for n in optionlist])
        return cls(filename, env_name, d)
    def __init__(self, filename, env_name, dict_):
        """create from a dict.

        If filename is not empty, search for config files at:
          /etc
          <path of this python file>
          $HOME
          <cwd>

        """
        self._dict= dict(dict_)
        self._filename= filename
        self._real_paths= []
        if not filename:
            self._paths= []
        else:
            search_paths= self.__class__.paths_from_env(env_name)
            if not search_paths:
                # not specified by environment variable:
                lib_path= os.path.dirname(os.path.abspath(__file__))
                search_paths=["/etc",
                              lib_path,
                              os.environ.get("HOME"),
                              os.getcwd()]
            self._paths= []
            for path in search_paths:
                if not path:
                    continue
                p= os.path.join(path, filename)
                if os.path.isfile(p):
                    self._paths.append(p)
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
    def _merge(self, dict_):
        """merge known keys from dict_ with self."""
        for (key, val) in dict_.items():
            if not self._dict.has_key(key):
                continue # silently ignore unknown keys
            if isinstance(self._dict[key], list):
                if not isinstance(val, list):
                    raise ValueError("error: config merge: expected a "
                                     "list at %s:%s" % (key,repr(val)))
                self._dict[key].extend(val)
            else:
                self._dict[key]= val
    def _load_file(self, filename, must_exist):
        """load filename.

        Note that the special key "#include" means that another config file is
        included much as with the #include directive in C.
        """
        def _load_lst(dict_, keys):
            """load lists from a dict."""
            l= []
            for k in keys:
                v= dict_.get(k)
                if not v:
                    continue
                l.extend(v)
                del dict_[k]
            return l
        if not os.path.exists(filename):
            if not must_exist:
                return
            raise IOError("error: file \"%s\" doesn't exist" % filename)
        self._real_paths.append(filename)
        data= sumolib.JSON.loadfile(filename)
        # pylint: disable=E1103
        #                     Instance of 'bool' has no 'items' member
        for f in _load_lst(data, ["#include", "#preload"]):
            self._load_file(f, must_exist= True)
        for f in _load_lst(data, ["#opt-preload"]):
            self._load_file(f, must_exist= False)
        self._merge(data)
        for f in _load_lst(data, ["#postload"]):
            self._load_file(f, must_exist= True)
        for f in _load_lst(data, ["#opt-postload"]):
            self._load_file(f, must_exist= False)
    def real_paths(self):
        """return the list of files that should be loaded or were loaded."""
        return self._real_paths
    def load(self, filenames):
        """load from all files in filenames list."""
        if filenames:
            for f in filenames:
                if os.path.isfile(f):
                    self._paths.append(f)
        for filename in self._paths:
            self._load_file(filename, must_exist= True)
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
            # in the option object, "-" in option names is always
            # replaced with "_":
            oobj_opt= opt.replace("-", "_")
            if not hasattr(option_obj, oobj_opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            val= getattr(option_obj, oobj_opt)
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
            oobj_opt= opt.replace("-", "_")
            if not hasattr(option_obj, oobj_opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            if val is not None:
                setattr(option_obj, oobj_opt, val)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
