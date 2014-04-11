# pylint: disable=C0302
#                          Too many lines in module
"""Utilities for the SUMO scripts.
"""

# pylint: disable=C0322
#                          Operator not preceded by a space
# pylint: disable=C0103
#                          Invalid name for type variable
import sys
import subprocess
import os
import os.path
import pprint
import copy
import re

_pyver= (sys.version_info[0], sys.version_info[1])

if _pyver < (2,5):
    sys.exit("ERROR: SUMO requires at least Python 2.5, "
             "your version is %d.%d" % _pyver)

try:
    import lockfile
    use_lockfile= True
except ImportError, _lockfile_err:
    if str(_lockfile_err) != 'No module named lockfile':
        raise
    else:
        sys.stderr.write("module 'lockfile' not found - " +\
                         "file accesses will not be locked\n")
        use_lockfile= False

# -----------------------------------------------
# JSON support
# -----------------------------------------------

if _pyver > (2,5):
    import json
    _JSON_TYPE= 1
elif _pyver == (2,5):
    # python 2.5 has no standard json module, assume that simplejson is
    # installed:
    try:
        import simplejson as json
    except ImportError, _json_err:
        sys.exit("ERROR: If SUMO is run with Python %d.%d "
                 "you need to have module 'simplejson' installed." % \
                 (sys.version_info[0],sys.version_info[1]))
    _JSON_TYPE= 0
else:
    # older python versions are already detected further above
    raise AssertionError("this shouldn't happen")

def json_dump_file(filename, var):
    """Dump a variable to a file in JSON format.
    """
    fh= open(filename, "w")
    if _JSON_TYPE==0:
        json.dump(var, fh, sort_keys= True, indent= 4*" ")
    else:
        json.dump(var, fh, sort_keys= True, indent= 4)
    fh.close()

# pylint: disable=C0303
#                          Trailing whitespace

def json_str(var):
    """convert a variable to JSON format.

    Here is an example:
    >>> var= {"key":[1,2,3], "key2":"val", "key3":{"A":1,"B":2}}
    >>> print json_str(var)
    {
        "key": [
            1, 
            2, 
            3
        ], 
        "key2": "val", 
        "key3": {
            "A": 1, 
            "B": 2
        }
    }
    """
    if _JSON_TYPE==0:
        return json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        return json.dumps(var, sort_keys= True, indent= 4) 

def json_dump(var):
    """Dump a variable in JSON format.

    Here is an example:
    >>> var= {"key":[1,2,3], "key2":"val", "key3":{"A":1,"B":2}}
    >>> json_dump(var)
    {
        "key": [
            1, 
            2, 
            3
        ], 
        "key2": "val", 
        "key3": {
            "A": 1, 
            "B": 2
        }
    }
    """
    print json_str(var)

# pylint: enable=C0303
#                          Trailing whitespace

def json_load(data):
    """decode a JSON string.
    """
    return json.loads(data)

def json_loadfile(filename):
    """load a JSON file.

    If filename is "-" read from stdin.
    """
    if filename != "-":
        fh= open(filename)
    else:
        fh= sys.stdin
    results= json.load(fh)
    if filename != "-":
        fh.close()
    return results

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
        self._list_append_opts= set()
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
    def set_list_append(self, name):
        """define an option to be of type "list append".

        In this case, command line options do not overwrite but append the
        list.
        """
        self._list_append_opts.add(name)
    def disable_default(self):
        """disable loading of the default file."""
        self.load_default= False
    def load(self, filenames):
        """first load self._filename, then filenames."""
        if self.load_default:
            lst= [self._filename]
        else:
            lst= []
        if filenames:
            lst.extend(filenames)
        for filename in lst:
            data= json_loadfile(filename)
            # pylint: disable=E1103
            #                     Instance of 'bool' has no 'items' member
            for (key, val) in data.items():
                if not self._dict.has_key(key):
                    continue # silently ignore unknown keys
                self._dict[key]= val
    def save(self, filename= None):
        """dump in json format"""
        # do not include "None" values:
        dump= {}
        for (k,v) in self._dict.items():
            if v is None:
                continue
            dump[k]= v
        if filename=="-":
            json_dump(dump)
            return
        if not filename:
            filename= self._filename
        json_dump_file(filename, dump)

    def merge_options(self, option_obj):
        """create from an option object."""
        for opt in self._dict.keys():
            if not hasattr(option_obj, opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            val= getattr(option_obj, opt)
            if val is not None:
                if self._dict[opt]:
                    if opt in self._list_append_opts:
                        self._dict[opt].extend(getattr(option_obj, opt))
                        continue
                self._dict[opt]= getattr(option_obj, opt)
        for (opt, val) in self._dict.items():
            if not hasattr(option_obj, opt):
                raise AssertionError(
                        "ERROR: key '%s' not in the option object" % opt)
            if val is not None:
                setattr(option_obj, opt, val)

# -----------------------------------------------
# tracing support
# -----------------------------------------------

def show_progress(cnt, cnt_max, message= None):
    """show progress on stderr.
    """
    if message:
        sys.stderr.write("'.' for every %s %s\n" % (cnt_max, message))
    cnt-= 1
    if cnt<0:
        sys.stderr.write(".")
        sys.stderr.flush()
        cnt= cnt_max
    return cnt

# -----------------------------------------------
# data structure utilities
# -----------------------------------------------

def opt_join(option, do_sort= False):
    """join command line option values to a single list.

    Here is an example:
    >>> a=["a b","c","d e f"]
    >>> opt_join(a)
    ['a', 'b', 'c', 'd', 'e', 'f']
    """
    if option is None:
        return
    lst= " ".join(option).split()
    if do_sort:
        lst.sort()
    return lst

def dict_of_sets_add(dict_, key, val):
    """add a key, create a set if needed.

    Here is an example:
    >>> import pprint
    >>> d= {}
    >>> dict_of_sets_add(d,"a",1)
    >>> dict_of_sets_add(d,"a",2)
    >>> dict_of_sets_add(d,"b",1)
    >>> pprint.pprint(d)
    {'a': set([1, 2]), 'b': set([1])}
    """
    l= dict_.get(key)
    if l is None:
        dict_[key]= set([val])
    else:
        l.add(val)

def dict_sets_to_lists(dict_):
    """change values from sets to sorted lists.

    Here is an example:
    >>> import pprint
    >>> d= {'a': set([1, 2]), 'b': set([1])}
    >>> ld= dict_sets_to_lists(d)
    >>> pprint.pprint(ld)
    {'a': [1, 2], 'b': [1]}
    """
    new= {}
    for (k,v) in dict_.items():
        new[k]= sorted(list(v))
    return new

# -----------------------------------------------
# basic system utilities
# -----------------------------------------------

def system(cmd, catch_stdout, catch_stderr, verbose, dry_run):
    """execute a command.

    execute a command and return the programs output
    may raise:
    IOError(errcode,stderr)
    OSError(errno,strerr)
    ValueError
    """
    if dry_run or verbose:
        print ">", cmd
        if dry_run:
            return None
    if catch_stdout:
        stdout_par=subprocess.PIPE
    else:
        stdout_par=None

    if catch_stderr:
        stderr_par=subprocess.PIPE
    else:
        stderr_par=None

    p= subprocess.Popen(cmd, shell=True,
                        stdout=stdout_par, stderr=stderr_par,
                        close_fds=True)
    (child_stdout, child_stderr) = p.communicate()
    # pylint: disable=E1101
    # "Instance 'Popen'has no 'returncode' member
    if p.returncode!=0:
        if stderr_par is not None:
            raise IOError(p.returncode,
                          "cmd \"%s\", errmsg \"%s\"" % (cmd,child_stderr))
        else:
            raise IOError(p.returncode,
                          "cmd \"%s\", rc %d" % (cmd, p.returncode))
    # pylint: enable=E1101
    return (child_stdout, child_stderr)

# -----------------------------------------------
# file locking
# -----------------------------------------------

def lock_a_file(filename, timeout=20):
    """lock a file.
    """
    timedelta= 5
    tries= timeout / timedelta
    if timeout % timedelta > 0:
        tries+= 1
    if not use_lockfile:
        return None
    lock= lockfile.LockFile(filename)
    # patch for not working lockfile module:
    lock.unique_name= "%s-%s" % (lock.unique_name, os.path.basename(filename))
    try_= 1
    while True:
        try_+= 1
        try:
            lock.acquire(timedelta)
            return lock
        except lockfile.Error,e:
            timeout-= timedelta
            if timeout>0:
                sys.stderr.write("waiting to aquire lock on "
                                 "file '%s' (%2d of %2d tries)...\n" % \
                                 (filename, try_, tries))
                continue
            extra= str(e)
            if extra:
                extra= " (%s)" % extra
            txt= ("File locking of file %s failed after %d seconds%s. "
                  "If you know that the file shouldn't be locked "
                  "you may try to remove the lockfiles.") % \
                 (filename, timeout, extra)
            raise AssertionError(txt)

def unlock_a_file(lock):
    """unlock a file.
    """
    if not use_lockfile:
        return
    if lock is None:
        raise AssertionError("unexpected: lock is None")
    lock.release()

def edit_with_lock(filename, verbose, dry_run):
    """lock a file, edit it, then unlock the file."""
    if not os.path.exists(filename):
        raise IOError("error: file \"%s\" doesn't exist" % filename)
    l= lock_a_file(filename)
    try:
        system("%s %s" % (os.environ["VISUAL"], filename),
               False, False, verbose, dry_run)
    except IOError, _:
        system("%s %s" % (os.environ["EDITOR"], filename),
               False, False, verbose, dry_run)
    unlock_a_file(l)

# -----------------------------------------------
# directory utilities
# -----------------------------------------------

# The following is needed in order to support python2.5
# where os.walk cannot follow symbolic links

def dirwalk(start_dir):
    """walk directories, follow symbolic links.

    Implemented to behave like os.walk
    On Python newer than 2.5 os.walk can follow symbolic links itself.
    """
    for (dirpath, dirnames, filenames) in os.walk(start_dir, topdown= True):
        yield (dirpath, dirnames, filenames)
        for dn in dirnames:
            p= os.path.join(dirpath, dn)
            if os.path.islink(p):
                for (dp, dn, fn) in dirwalk(p):
                    yield (dp, dn, fn)

# -----------------------------------------------
# version and path support
# -----------------------------------------------

def contains_treetag(path):
    """returns True if the path looks like it contains a treetag."""
    return "+" in path

def split_treetag(path):
    """split a path into head,treetag.

    A path like /opt/Epics/R3.14.8/support/BIIcsem/1-0+001
    is splitted to
    "/opt/Epics/R3.14.8/support/BIIcsem/1-0","001"

    Here is an example:
    >>> split_treetag("abc/def/1-0")
    ['abc/def/1-0', '']
    >>> split_treetag("abc/def/1-0+001")
    ['abc/def/1-0', '001']
    """
    l= path.rsplit("+",1)
    if len(l)<2:
        l.append("")
    return l

def rev2key(rev):
    """convert a revision number to a comparable string.

    This is needed to compare darcs revision tags.

    Examples of valid revisions:

      2.3.4
      2-3-4
      R2-3-4
      seq-2.3.4
      head
      trunk

    Here are some examples:
    >>> rev2key("R2-3-4")
    '002.003.004'
    >>> rev2key("2-3-4")
    '002.003.004'
    >>> rev2key("head")
    '-head'
    >>> rev2key("test")
    '-test'
    >>> rev2key("test")<rev2key("R2-3-4")
    True
    >>> rev2key("R2-3-3")<rev2key("R2-3-4")
    True
    >>> rev2key("R2-3-5")<rev2key("R2-3-4")
    False
    >>> rev2key("R2-4-3")<rev2key("R2-3-4")
    False
    >>> rev2key("R1-3-4")<rev2key("R2-3-4")
    True
    >>> rev2key("R3-3-4")<rev2key("R2-3-4")
    False
    """

    if rev=="":
        return "-"
    t= tag2version(rev)
    if not t[0].isdigit():
        return "-" + rev
    rev= t
    # allow "-" and "." as separator for numbers:
    rev= rev.replace("-",".")
    l= rev.split(".")
    n= []
    # reformat all numbers in a 3-digit form:
    for e in l:
        try:
            n.append("%03d" % int(e))
        except ValueError, _:
            n.append(str(e))
    return ".".join(n)

def split_path(path):
    """split a path into (base, version, treetag).

    Here are some examples:
    >>> split_path("abc/def/1-3+001")
    ['abc/def', '1-3', '001']
    >>> split_path("abc/def/1-3")
    ['abc/def', '1-3', '']
    >>> split_path("abc/def/head+002")
    ['abc/def', 'head', '002']
    """
    (head,tail)= os.path.split(path)
    (version, treetag)= split_treetag(tail)
    return [head, version, treetag]

def tag2version(ver):
    """convert a tag to a version.

    Here are some examples:
    >>> tag2version("1-2")
    '1-2'
    >>> tag2version("R1-2")
    '1-2'
    >>> tag2version("R-1-2")
    '1-2'
    >>> tag2version("seq-1-2")
    '1-2'
    >>> tag2version("head")
    'head'
    >>> tag2version("")
    ''
    """
    if len(ver)<1:
        return ver
    mode=0
    for i in xrange(len(ver)):
        if mode==0:
            if ver[i].isalpha():
                continue
            mode=1
        if mode==1:
            if ver[i]=="-" or ver[i]=="_":
                mode=2
                continue
            mode=2
        if mode==2:
            if ver[i].isdigit():
                return ver[i:]
            else:
                return ver
    return ver

def version2tag(tag):
    """convert a version to a darcs tag.

    (according to BESSY conventions)
    """
    if not tag:
        return
    if tag[0].isdigit():
        return "R"+tag
    return tag

def is_standardpath(path, darcs_tag):
    """checks if path is complient to Bessy convention for support paths.

    Here are some examples:
    >>> is_standardpath("support/mcan/2-3", "R2-3")
    True
    >>> is_standardpath("support/mcan/2-3", "R2-4")
    False
    >>> is_standardpath("support/mcan/head", "R2-3")
    False
    >>> is_standardpath("support/mcan/2-3+001", "R2-3")
    True
    """
    l= split_path(path)
    return tag2version(l[1])==tag2version(darcs_tag)

def scan_source_spec(elms):
    """scan a source specification.

    A sourcespec is a list of strings in the form ["path",PATH] or
    ["darcs",URL] or ["darcs",URL,TAG].

    Here are some examples:

    >>> scan_source_spec(["path","ab"])
    {'path': 'ab'}
    >>> scan_source_spec(["path"])
    Traceback (most recent call last):
        ...
    ValueError: invalid source spec: '['path']'
    >>> scan_source_spec(["path","a","b"])
    Traceback (most recent call last):
        ...
    ValueError: invalid source spec: '['path', 'a', 'b']'
    >>> scan_source_spec(["darcs","abc"])
    {'darcs': {'url': 'abc'}}
    >>> scan_source_spec(["darcs","abc","R1-2"])
    {'darcs': {'url': 'abc', 'tag': 'R1-2'}}
    >>> scan_source_spec(["darcs"])
    Traceback (most recent call last):
        ...
    ValueError: invalid source spec: '['darcs']'
    >>> scan_source_spec(["darcs","abc","R1-2","xy"])
    Traceback (most recent call last):
        ...
    ValueError: invalid source spec: '['darcs', 'abc', 'R1-2', 'xy']'
    """
    if elms[0]=="path":
        if len(elms)!=2:
            raise ValueError("invalid source spec: '%s'" % repr(elms))
        return {"path": elms[1]}
    if elms[0]=="darcs":
        if len(elms)==2:
            return {"darcs":{"url":elms[1]}}
        elif len(elms)==3:
            return {"darcs":{"url":elms[1], "tag":elms[2]}}
        else:
            raise ValueError("invalid source spec: '%s'" % repr(elms))
    raise ValueError("invalid source spec: '%s'" % repr(elms))

def create_module_arch_spec(modulename, versionname, default_archs= None):
    """create a module arch spec string from modulename, versionname, arch.

    This function returns a string that can be parsed by scan_module_arch_spec.

    """
    elms= [modulename, versionname]
    if default_archs is not None:
        elms.extend(sorted(default_archs))
    return ":".join(elms)

# pylint: disable=C0301
#                          Line too long

def scan_module_arch_spec(spec, default_archs=None):
    """parse a module specification.

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
       arch              : set exactly these archs

    returns a tuple (modulename, moduledict) where moduledict is:
      {
        "version"     : <version>
        "version_flag": "==" or ">=" or "<="
        "archs"       : <set of archs>
      }

    Note that the returned moduledict contains "==" as equality flag, not "=".
    This means that versions must match the version string *exactly*, e.g.
    "R1-3" and "1-3" would not match.

    Here are some examples:

    >>> import pprint
    >>> pprint.pprint(scan_module_arch_spec("ALARM"))
    ('ALARM', {})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:R3-5"))
    ('ALARM', {'version': 'R3-5', 'version_flag': '=='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:+R3-5"))
    ('ALARM', {'version': 'R3-5', 'version_flag': '>='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:-R3-5"))
    ('ALARM', {'version': 'R3-5', 'version_flag': '<='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:+"))
    ('ALARM', {'version': '', 'version_flag': '>='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:-"))
    ('ALARM', {'version': '', 'version_flag': '<='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:-R3-5:linux-x86"))
    ('ALARM',
     {'archs': set(['linux-x86']), 'version': 'R3-5', 'version_flag': '<='})
    >>> pprint.pprint(scan_module_arch_spec("ALARM::linux-x86"))
    ('ALARM', {'archs': set(['linux-x86'])})
    >>> pprint.pprint(scan_module_arch_spec("ALARM:-R3-5:+linux-x86",
    ...                                     ["vxWorks-ppc603"]))
    ('ALARM',
     {'archs': set(['linux-x86', 'vxWorks-ppc603']),
      'version': 'R3-5',
      'version_flag': '<='})
    >>> pprint.pprint(scan_module_arch_spec(
    ...        "ALARM:-R3-5:-vxWorks-mv162:+vxWorks-ppc603",
    ...        ["linux-x86","vxWorks-mv162"]))
    ('ALARM',
     {'archs': set(['linux-x86', 'vxWorks-ppc603']),
      'version': 'R3-5',
      'version_flag': '<='})
    """
    # pylint: disable=R0912
    #                          Too many branches
    modulename= None
    version= None
    if default_archs is None:
        archs= set()
    else:
        archs= set(default_archs)
    for l in spec.split(":"):
        if modulename is None:
            modulename= l
            continue
        if version is None:
            if l=="":
                version= ()
                continue
            if l[0]=="-":
                version= (l[1:], "<=")
            elif l[0]=="+":
                version= (l[1:], ">=")
            else:
                version= (l, "==")
            continue
        if l[0]=="+":
            archs.add(l[1:])
            continue
        elif l[0]=="-":
            archs.discard(l[1:])
            continue
        else:
            archs= set([l])
            continue
    d= {}
    if version:
        d["version"]= version[0]
        d["version_flag"]= version[1]
    if archs:
        d["archs"]= archs
    return (modulename,d)

# pylint: enable=C0301

def scan_module_arch_specs(specs, default_archs= None):
    """scan a list of module specification strings.

    returns a list of tuples (modulename, moduledict).

    Note that if a modulename is used twice, the later definition overwrites
    the first one. However, the module retains it's position in the list of
    modules.

    A spec in the form "modulename:-" means that this is removed from the list
    of modules even if it was mentioned before.
    """
    module_order= []
    dict_= {}
    for s in specs:
        (modulename, moduledict)= scan_module_arch_spec(s, default_archs)
        version= moduledict.get("version")
        if version=="":
            if moduledict["version_flag"]=="<=":
                # "module:-" means "remove module from list
                if dict_.has_key(modulename):
                    del dict_[modulename]
                    module_order.remove(modulename)
                continue
        if not dict_.has_key(modulename):
            module_order.append(modulename)
        dict_[modulename]= moduledict
    lst= []
    for modulename in module_order:
        lst.append((modulename, dict_[modulename]))
    return lst

def compare_versions_flag(flag, version1, version2):
    """compare versions according to given flag.

    A <None> as version matches any other version.

    Note that there are two ways to test equality, one where the version
    strings must match exactly and one where only the version numbers must
    match. We use the flags "==" and "=" to distinguish these. Here is the
    meaning:

    ==  : match exactly, so "R1-3" is different from "1-3"
    =   : match the version number, so "R1-3" is equal to "1-3".

    Here are some examples:
    >>> compare_versions_flag("==", None, "R1-3")
    True
    >>> compare_versions_flag("==", "R1-2", None)
    True
    >>> compare_versions_flag("==", "R1-2", "R1-3")
    False
    >>> compare_versions_flag("==", "R1-2", "R1-2")
    True
    >>> compare_versions_flag("==", "R1-2", "1-2")
    False
    >>> compare_versions_flag("=", "R1-2", "1-2")
    True
    >>> compare_versions_flag("<=", "R1-2", "1-2")
    True
    >>> compare_versions_flag("<=", "R1-1", "R1-2")
    True
    >>> compare_versions_flag("<=", "R1-3", "R1-2")
    False
    >>> compare_versions_flag(">=", "R1-1", "R1-2")
    False
    >>> compare_versions_flag(">=", "R1-2", "R1-2")
    True
    >>> compare_versions_flag(">=", "R1-3", "R1-2")
    True
    """
    if version1 is None:
        return True
    if version2 is None:
        return True
    if flag=="==":
        return (version1==version2)
    k1= rev2key(version1)
    k2= rev2key(version2)
    if flag=="=":
        return (k1==k2)
    if flag=="<=":
        return (k1<=k2)
    if flag==">=":
        return (k1>=k2)
    raise AssertionError("unknown flag: %s" % flag)

# -----------------------------------------------
# string utilities
# -----------------------------------------------

def guess_string(st, allowed):
    """guess a string that is abbreviated.

    Allowed should be a set of allowed strings. The function tries to find a
    unique string in allowed that starts with the same characters as st and
    returns it. Returns None if no unoue match was found.
    """
    match= None
    for s in allowed:
        if s.startswith(st):
            if match is not None:
                return None
            match= s
    return match

# -----------------------------------------------
# generic datastructure utilities
# -----------------------------------------------

def single_key(dict_):
    """dict must have exactly one key, return it.

    Raises ValueError if the dict has more than one key.
    """
    keys= dict_.keys()
    if len(keys)!=1:
        raise ValueError("dict hasn't exactly one key: %s" % repr(keys))
    return keys[0]

def single_key_item(dict_):
    """dict must have exactly one key, return it and it's value.

    Raises ValueError if the dict has more than one key.
    """
    k= single_key(dict_)
    return (k, dict_[k])

def dict_update(dict_, other, keylist= None):
    """update dict_ with other but do not change existing values.

    If keylist is given, update only these keys.
    """
    if keylist is None:
        keylist= other.keys()
    for k in keylist:
        v= other[k]
        old_v= dict_.get(k)
        if old_v is None:
            dict_[k]= v
            continue
        if old_v==v:
            continue
        raise ValueError("key %s: contradicting values: %s %s" % \
                          (k,repr(old_v),repr(v)))

def uniq_dict_update(dict_, other):
    """update dict_ with other but do not change existing values.

    The dict must have a single key.

    """
    keys= dict_.keys()
    if len(keys)>1:
        raise ValueError("dict has more than one key: %s" % repr(dict_))
    okeys= other.keys()
    if len(okeys)>1:
        raise ValueError("other dict has more than one key: %s" % repr(other))
    if keys[0]!=okeys[0]:
        raise ValueError("dicts have different keys: %s %s" % \
                         (keys[0], okeys[0]))

    keylist= other.keys()
    for k in keylist:
        v= other[k]
        old_v= dict_.get(k)
        if old_v is None:
            dict_[k]= v
            continue
        if old_v==v:
            continue
        raise ValueError("key %s: contradicting values: %s %s" % \
                          (k,repr(old_v),repr(v)))

def list_update(list1, list2):
    """update a list with another.

    In the returned list each element is unique and it is sorted.
    """
    if not list1:
        return sorted(list2[:])
    s= set(list1)
    s.update(list2)
    return sorted(s)

# -----------------------------------------------
# classes
# -----------------------------------------------

class RegexpMatcher(object):
    """apply one or more regexes on strings."""
    def __init__(self, regexes=None):
        r"""initialize from a list of regexes.

        Here is a simple example:
        >>> rx= RegexpPatcher(((r"a(\w+)",r"a(\1)"),(r"x+",r"x")))
        >>> rx.apply("ab xx")
        'a(b) x'
        """
        self._list= []
        if regexes is not None:
            for rx in regexes:
                self.add(rx)
    def add(self, regexp):
        """add a regexp."""
        #print "RX: ",repr(regexp_pair)
        rx= re.compile(regexp)
        self._list.append(rx)
    def match(self, str_):
        """match the regular expression to a string"""
        if not self._list:
            return False
        for rx in self._list:
            if rx.match(str_):
                return True
        return False
    def search(self, str_):
        """search the regular expression in a string"""
        if not self._list:
            return False
        for rx in self._list:
            if rx.search(str_):
                return True
        return False

class RegexpPatcher(object):
    """apply one or more regexes on strings."""
    def __init__(self, tuples=None):
        r"""initialize from a list of tuples.

        Here is a simple example:
        >>> rx= RegexpPatcher(((r"a(\w+)",r"a(\1)"),(r"x+",r"x")))
        >>> rx.apply("ab xx")
        'a(b) x'
        """
        self._list= []
        if tuples is not None:
            for regexp_pair in tuples:
                self.add(regexp_pair)
    def add(self, regexp_pair):
        """add a from-regexp to-regexp pair."""
        #print "RX: ",repr(regexp_pair)
        rx= re.compile(regexp_pair[0])
        self._list.append((rx, regexp_pair[1]))
    def apply(self, str_):
        """apply the regular expressions to a string"""
        if not self._list:
            return str_
        for (rx, repl) in self._list:
            str_= rx.sub(repl, str_)
        return str_

class Hints(object):
    """Combine hints for sumo-scan"""
    _empty= {}
    def __init__(self, specs= None):
        r"""initialize from a list of specification strings.

        Here is an example:
        >>> h= Hints()
        >>> h.add(r'\d,TAGLESS')
        >>> print h.flags("ab")
        {}
        >>> print h.flags("ab12")
        {'tagless': True}
        """
        self._hints= []
        if specs is not None:
            for spec in specs:
                self.add(spec)
    def add(self, spec):
        """add a new hint."""
        parts= spec.split(",")
        rx= re.compile(parts[0])
        d= {}
        for flag in parts[1:]:
            # pylint: disable=W0212
            #         Access to a protected member
            (key,val)= self.__class__._parse_flag(flag)
            d[key]= val
        self._hints.append((rx, d))
    @staticmethod
    def _parse_flag(flag):
        """parse a flag string."""
        if flag=="PATH":
            return ("path", True)
        if flag=="TAGLESS":
            return ("tagless", True)
        raise ValueError("unknown flag: %s" % flag)
    def flags(self, path):
        """return the flags of a path."""
        for (rx, d) in self._hints:
            if rx.search(path):
                return d
        # pylint: disable=W0212
        #         Access to a protected member
        return self.__class__._empty

class JSONstruct(object):
    """an object that is a python structure.

    This is a dict that contains other dicts or lists or strings or floats or
    integers.
    """
    def selfcheck(self, msg):
        """raise an exception if the object is not valid."""
        # pylint: disable=W0613
        #                          Unused argument
        # pylint: disable=R0201
        #                          Method could be a function
        return
    def __init__(self, dict_= None):
        """create the object."""
        if dict_ is None:
            self.dict_= {}
        else:
            self.dict_= dict_
        self.lock= None
        self.lock_filename= None
    def lock_file(self, filename):
        """lock a file and store filename and lock in the object."""
        if self.lock_filename==filename:
            # already locked
            return
        self.unlock_file()
        self.lock= lock_a_file(filename)
        self.lock_filename= filename
    def unlock_file(self):
        """remove a filelock if there is one."""
        if self.lock_filename is not None:
            unlock_a_file(self.lock)
            self.lock= None
            self.lock_filename= None
    def __del__(self):
        """object destructor."""
        self.unlock_file()
    def datadict(self):
        """return the internal dict."""
        return self.dict_
    def to_dict(self):
        """return the object as a dict."""
        return self.dict_
    def __repr__(self):
        """return a repr string."""
        return "%s(%s)" % (self.__class__.__name__, repr(self.to_dict()))
    def __str__(self):
        """return a human readable string."""
        txt= ["%s:" % self.__class__.__name__]
        txt.append(pprint.pformat(self.to_dict(), indent=2))
        return "\n".join(txt)
    @classmethod
    def from_json(cls, json_data):
        """create an object from a json string."""
        obj= cls(json_load(json_data))
        obj.selfcheck("(created from JSON string)")
        return obj
    @classmethod
    def from_json_file(cls, filename, keep_locked= False):
        """create an object from a json file."""
        if filename=="-":
            result= cls(json_loadfile(filename))
            result.selfcheck("(created from JSON string on stdin)")
            return result
        if not os.path.exists(filename):
            raise IOError("file \"%s\" not found" % filename)
        l= lock_a_file(filename)
        result= cls(json_loadfile(filename))
        if keep_locked:
            result.lock= l
            result.lock_filename= filename
        else:
            unlock_a_file(l)
        result.selfcheck("(created from JSON file %s)" % filename)
        return result
    def json_string(self):
        """return a JSON representation of the object."""
        return json_str(self.to_dict())
    def json_print(self):
        """print a JSON representation of the object."""
        print self.json_string()
    def json_save(self, filename, verbose, dry_run):
        """save as a JSON file."""
        if not filename:
            raise ValueError("filename is empty")
        if filename=="-":
            raise ValueError("filename must not be \"-\"")
        backup= "%s.bak" % filename
        if not dry_run:
            self.lock_file(filename)
        if os.path.exists(backup):
            if verbose:
                print "remove %s" % backup
            if not dry_run:
                os.remove(backup)
        if os.path.exists(filename):
            if verbose:
                print "rename %s to %s" % (filename, backup)
            if not dry_run:
                os.rename(filename, backup)
        if not dry_run:
            json_dump_file(filename, self.to_dict())
        if not dry_run:
            self.unlock_file()

class PathSource(JSONstruct):
    """the structure that holds the source information for a path."""
    def __init__(self, dict_= None):
        """create the object."""
        super(PathSource, self).__init__(dict_)
    def add_path(self, path, source):
        """add a simple path."""
        self.datadict()[path]= {"path": source}
    def add_darcs(self, path, url, tag= None):
        """add darcs repository information."""
        if tag is None:
            self.datadict()[path]= {"darcs": {"url": url}}
        else:
            self.datadict()[path]= {"darcs": {"url": url, "tag": tag}}
    def iterate(self):
        """iterate on all items."""
        return self.datadict().iteritems()
    def filter_no_repos(self):
        """return a new object where "path" enities are removed."""
        new= self.__class__()
        for path, data in self.iterate():
            k= single_key(data)
            if k!="path":
                new.datadict()[path]= data
        return new
    def filter_no_tags(self):
        """return a new object containing repos without tags."""
        new= self.__class__()
        for path, data in self.iterate():
            k= single_key(data)
            if k=="path":
                continue
            dict_= data[k]
            if not dict_.has_key("tag"):
                new.datadict()[path]= data
        return new
    def get_struct(self, path):
        """return data as a structure."""
        return self.datadict()[path]
    def get_data(self, path):
        """return data for a given path.

        Returns a tuple:
          (type, data)

        For type=="darcs" the data is:
          { "url": url, "tag": tag }

        for type=="path" the data is:
          path

        type: repository type, e.g. "darcs"
        url : the url where to get
        tag : the repository tag, may be omitted

        Note: raises KeyError if path doesn't exist
        """
        data= self.datadict()[path]
        return single_key_item(data)

class Dependencies(JSONstruct):
    """the dependency database."""
    # pylint: disable=R0904
    #                          Too many public methods
    # pylint: disable=R0913
    #                          Too many arguments
    states_list= ["stable", "testing", "unstable"]
    states_dict= dict(zip(states_list,range(len(states_list))))
    @classmethod
    def _min_state(cls, state_list):
        """return the minimum of a list of states."""
        i= min([cls.states_dict[s] for s in state_list])
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
                          constant_src_state= None):
        """intelligent merge of dependency dicts.

        If a dependency exists, take the "smaller" state as new state, if it
        doesn't exist, just take it.

        If constant_src_state is given take this instead of the
        state actually found in src_deps.
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
                dest_dep_dict[src_ver]= cls._min_state((src_state, dest_state))
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
    def merge(self, other, constant_src_state= None):
        """merge another Dependencies object to self."""
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
                            vdict[dictname]= self.__class__._min_state(
                                    (vdict[dictname], src_state))
                        else:
                            vdict[dictname]= src_state
                        # pylint: enable=W0212
                        continue
                    if dictname=="archs":
                        try:
                            dict_update(vdict.setdefault(dictname,{}),
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
                            dict_update(vdict.setdefault(dictname,{}),
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
                                constant_src_state)
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
    def set_source(self, module_name, versionname, repo_dict):
        """add a module with source spec, state and archs."""
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        version["source"]= repo_dict
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
        if not self.__class__.states_dict.has_key(state):
            raise ValueError("invalid state: %s" % state)
        m_dict= self.datadict()[modulename]
        dep_dict= m_dict[versionname].setdefault("dependencies",{})
        dep_module_dict= dep_dict.setdefault(dep_modulename, {})
        dep_module_dict[dep_versionname]= state
    def del_dependency(self, modulename, versionname,
                       dep_modulename, dep_versionname):
        """delete dependency for a module:version if it exists.
        """
        m_dict= self.datadict()[modulename]
        dep_dict= m_dict[versionname].get("dependencies")
        if dep_dict is None:
            return
        dep_module_dict= dep_dict.get(dep_modulename)
        if dep_module_dict is None:
            return
        if dep_module_dict.has_key(dep_versionname):
            del dep_module_dict[dep_versionname]
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
        return single_key_item(l)
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
                    if not((dep_name,dep_version) in modules_set):
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
        dep_list.sort(key= rev2key, reverse= True)
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
                      key= rev2key,
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
        (_, sourcedata)= single_key_item(d["source"])
        if isinstance(sourcedata, dict):
            if sourcedata.has_key("tag"):
                if sourcedata["tag"]== versionname:
                    sourcedata["tag"]= newversionname
            else:
                # cannot patch tag, invalidate the source spec:
                sourcedata["url"]= ""
        else:
            # invalidate the source date
            sourcedata= ""
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
                if not compare_versions_flag("==",version,
                                             versionname):
                    continue
                d[version]= self.datadict()[modulename][version]
        return new
    def partial_copy_by_specdict(self, specdict):
        """take items from the Dependencies object and create a new one.

        specdict must be a dict mapping modulenames to a dict as returned by
        scan_module_arch_spec.

        Note that this function treats versions like "R1-3" and "1-3" to be
        different.

        If no versions are defined for a module, take all versions.
        If no archs are defined, take all archs.

        When no moduleversions are found, rause a ValueError exception.

        Note that the new Dependencies object only contains references of the
        data. This DOES NOT do a deep copy.
        """
        new= self.__class__()
        for modulename, spec_dict in specdict.items():
            d= new.datadict().setdefault(modulename, {})
            archs= spec_dict.get("archs")
            match_version= spec_dict.get("version")
            match_flag   = spec_dict.get("version_flag")
            # scan stable, testing and unstable versions:
            for version in self.iter_versions(modulename, "unstable",
                                              archs, must_exist= True):
                if not compare_versions_flag(match_flag,version,
                                             match_version):
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
                dep_no= 0
                for dep_name in self.iter_dependencies(modulename,
                                                       versionname):
                    for dep_ver in self.iter_dependency_versions(modulename,
                                                                 versionname,
                                                                 dep_name,
                                                                 "unstable",
                                                                 None):
                        dep_no+= 1
                        if not (dep_name,dep_ver) in modules:
                            deletions.append((dep_name, dep_ver))
                if len(deletions)>= dep_no:
                    raise ValueError("error: dependencies for %s:%s are "
                                     "not part of the DB file" % \
                                     (modulename, versionname))
                for (dep_name, dep_ver) in deletions:
                    self.del_dependency(modulename, versionname,
                                        dep_name, dep_ver)

class Builddb(JSONstruct):
    """the buildtree database."""
    # pylint: disable=R0904
    #                          Too many public methods
    states= set(("stable","testing","unstable"))
    @classmethod
    def guess_state(cls,st):
        """convert an abbreviation to a valid state."""
        errst= "error: cannot determine what state is meant by %s" % st
        match= guess_string(st, cls.states)
        if match is None:
            errst= "error: cannot determine what state is meant by %s" % st
            raise ValueError(errst)
        return match
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
    def generate_buildtag(self):
        """generate a new buildtag that is not already in the Builddb."""
        no= None
        for b in self.iter_builds():
            if b.startswith("AUTO-"):
                b= b.replace("AUTO-","")
                try:
                    n= int(b)
                except ValueError, _:
                    continue
                if n>no:
                    no= n
        if no is None:
            no= 0
        no+= 1
        return "AUTO-%03d" % no
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
        data= json_loadfile(filename)
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
        if state not in self.__class__.states:
            raise ValueError("not an allowed state: %s" % state)
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
    def state(self, build_tag):
        """return the state of the build."""
        d= self.datadict()
        return d[build_tag]["state"]
    def change_state(self, build_tag, new_state):
        """sets the state to a new value."""
        if new_state not in self.__class__.states:
            raise ValueError("not an allowed state: %s" % new_state)
        d= self.datadict()
        d[build_tag]["state"]= new_state
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
    def filter_by_specdict(self, specdict, db):
        """return a new Builddb that satisfies the given list of specs.

        Note that this function treats versions like "R1-3" and "1-3" to be
        different.
        """
        new= self.__class__()
        for build_tag in self.iter_builds():
            found= True
            m= self.modules(build_tag)
            for (modulename,modulespec) in specdict.items():
                v= m.get(modulename)
                if v is None:
                    found= False
                    break
                if not compare_versions_flag(modulespec.get("version_flag"),
                                             v,modulespec.get("version")):
                    found= False
                    break
                if not db.check_archs(modulename, v, modulespec.get("archs")):
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
        scan_module_arch_spec.
        """
        lst= []
        build_dict= self.modules(build_tag)
        for modulename in sorted(build_dict.keys()):
            versionname= build_dict[modulename]
            lst.append(create_module_arch_spec(modulename, versionname,
                       default_archs))
        return lst

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
