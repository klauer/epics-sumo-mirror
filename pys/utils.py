"""Utilities for the pysupport scripts.
"""
# pylint: disable=C0302
#                          Too many lines in module
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

try:
    import lockfile
    use_lockfile= True
except ImportError, _lockfile_err:
    if _lockfile_err.message != 'No module named lockfile':
        raise
    else:
        sys.stderr.write("module 'lockfile' not found - " +\
                         "file accesses will not be locked\n")
        use_lockfile= False

# -----------------------------------------------
# JSON support
# -----------------------------------------------

if sys.version_info[0]>2 or (sys.version_info[0]==2 and sys.version_info[1]>5):
    import json
    _JSON_TYPE= 1
else:
    import simplejson as json
    _JSON_TYPE= 0

def json_dump_file(filename, var):
    """Dump a variable to a file in JSON format.
    """
    fh= open(filename, "w")
    if _JSON_TYPE==0:
        json.dump(var, fh, sort_keys= True, indent= 4*" ")
    else:
        json.dump(var, fh, sort_keys= True, indent= 4)
    fh.close()

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

def system(cmd, catch_stdout, verbose, dry_run):
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

    p= subprocess.Popen(cmd, shell=True,
                        stdout=stdout_par, stderr=subprocess.PIPE,
                        close_fds=True)
    (child_stdout, child_stderr) = p.communicate()
    # pylint: disable=E1101
    # "Instance 'Popen'has no 'returncode' member
    if p.returncode!=0:
        raise IOError(p.returncode,
                      "cmd \"%s\", errmsg \"%s\"" % (cmd,child_stderr))
    # pylint: enable=E1101
    return(child_stdout)

# -----------------------------------------------
# file locking
# -----------------------------------------------

def lock_a_file(filename, timeout=20):
    """lock a file.
    """
    if not use_lockfile:
        return None
    lock= lockfile.LockFile(filename)
    # patch for not working lockfile module:
    lock.unique_name= "%s-%s" % (lock.unique_name, os.path.basename(filename))
    try:
        lock.acquire(timeout)
    except lockfile.Error,e:
        txt= ("File locking of file %s failed after % seconds with "
              "error %s. If you know that the file shouldn't be locked "
              "you may try to remove the lockfile.") % \
             (filename, timeout, str(e))
        raise AssertionError, txt
    return lock

def unlock_a_file(lock):
    """unlock a file.
    """
    if not use_lockfile:
        return
    if lock is None:
        raise AssertionError, "unexpected: lock is None"
    lock.release()

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
      ,2-3-4
      /2-3-4
      head
      trunk

    Here are some examples:
    >>> rev2key("R2-3-4")
    '002.003.004'
    >>> rev2key("2-3-4")
    '002.003.004'
    >>> rev2key("/2-3-4")
    '002.003.004'
    >>> rev2key(",R2-3-4")
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
    if not rev: # empty string
        return "-"
    if (rev[0]== "/") or (rev[0]==","):
        # remove leading "/" or ",":
        if len(rev)<=1:
            return "-"
        rev= rev[1:]
    if len(rev)>1:
        # remove leading "R" if it is followed by a digit:
        if rev[0]=="R" and rev[1].isdigit():
            rev= rev[1:]
    # if first character is not a digit, return string prepended with a "-".
    # This ensures that revision strings with a digit will come after such a
    # string.
    if not rev[0].isdigit():
        return "-"+rev
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

def tag2version(tag):
    """convert a darcs tag to a version.

    (according to BESSY conventions)
    """
    if len(tag)<2:
        return tag
    if tag[0]=="R" and tag[1].isdigit():
        return tag[1:]
    return tag

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

def scan_modulespec(spec):
    """parse a module specification.

    A module specification has the form:

      modulename                : any version
      modulename:versionname    : exactly this version
      modulename:+versionname   : this version or newer
      modulename:-versionname   : this version or older

    returns a tuple:
      (modulename,flag,versionname) 
      
    which flag: "any", "this", "this_or_newer", "this_or_older"

    Here are some examples:
    >>> scan_modulespec("ALARM")
    ('ALARM', 'any', '')
    >>> scan_modulespec("ALARM:R3-5")
    ('ALARM', 'this', 'R3-5')
    >>> scan_modulespec("ALARM:-R3-5")
    ('ALARM', 'this_or_older', 'R3-5')
    >>> scan_modulespec("ALARM:+R3-5")
    ('ALARM', 'this_or_newer', 'R3-5')
    """
    l= spec.split(":")
    if len(l)<=1:
        return (spec, "any", "")
    if l[1][0]=="-":
        return (l[0], "this_or_older", l[1][1:])
    if l[1][0]=="+":
        return (l[0], "this_or_newer", l[1][1:])
    return (l[0], "this", l[1])

def compare_versions_flag(flag, version1, version2):
    """compare versions according to given flag.

    Here are some examples:
    >>> compare_versions_flag("any", "R1-2", "R1-3")
    True
    >>> compare_versions_flag("this", "R1-2", "R1-3")
    False
    >>> compare_versions_flag("this", "R1-2", "R1-2")
    True
    >>> compare_versions_flag("this", "R1-2", "1-2")
    True
    >>> compare_versions_flag("this_or_older", "R1-2", "1-2")
    True
    >>> compare_versions_flag("this_or_older", "R1-1", "R1-2")
    True
    >>> compare_versions_flag("this_or_older", "R1-3", "R1-2")
    False
    >>> compare_versions_flag("this_or_newer", "R1-1", "R1-2")
    False
    >>> compare_versions_flag("this_or_newer", "R1-2", "R1-2")
    True
    >>> compare_versions_flag("this_or_newer", "R1-3", "R1-2")
    True
    """
    if flag=="any":
        return True
    k1= rev2key(version1)
    k2= rev2key(version2)
    if flag=="this":
        return (k1==k2)
    if flag=="this_or_older":
        return (k1<=k2)
    if flag=="this_or_newer":
        return (k1>=k2)
    raise AssertionError, "unknown flag: %s" % flag

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
        raise ValueError, "key %s: contradicting values: %s %s" % \
                          (k,repr(old_v),repr(v))

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

class JSONstruct(object):
    """an object that is a python structure.
    
    This is a dict that contains other dicts or lists or strings or floats or
    integers.
    """
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
        return cls(json_load(json_data))
    @classmethod
    def from_json_file(cls, filename, keep_locked= False):
        """create an object from a json file."""
        if filename=="-":
            return cls(json_loadfile(filename))
        if not os.path.exists(filename):
            raise IOError, "file \"%s\" not found" % filename
        l= lock_a_file(filename)
        result= cls(json_loadfile(filename))
        if keep_locked:
            result.lock= l
            result.lock_filename= filename
        else:
            unlock_a_file(l)
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
            raise ValueError, "filename is empty"
        if filename=="-":
            raise ValueError, "filename must not be \"-\""
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
    def add_path(self, path):
        """add a simple path."""
        self.datadict()[path]= ["path", path]
    def add_darcs(self, path, url, tag= None):
        """add darcs repository information."""
        if tag is None:
            self.datadict()[path]= ["darcs", url]
        else:
            self.datadict()[path]= ["darcs", url, tag]
    def iterate(self):
        """iterate on all items."""
        return self.datadict().iteritems()
    def filter_no_repos(self):
        """return a new object where "path" enities are removed."""
        new= self.__class__()
        for path, data in self.iterate():
            if data[0]!="path":
                new.datadict()[path]= data
        return new
    def filter_no_tags(self):
        """return a new object containing repos without tags."""
        new= self.__class__()
        for path, data in self.iterate():
            if data[0]=="path":
                continue
            if len(data)<3:
                new.datadict()[path]= data
        return new
    def get_struct(self, path):
        """return data as a structure."""
        return self.datadict()[path]
    def get(self, path):
        """return data for a given path.

        Returns:
          (type, url, tag)

        type: "path" or "darcs" 
        url : the url where to get
        tag : the repository tag, may be empty ("").

        Note: raises KeyError if path doesn't exist
        """
        d= self.datadict()[path]
        if len(d)>2:
            return tuple(d)
        else:
            return (d[0], d[1], "")

# pylint: disable=R0904
#                          Too many public methods
# pylint: disable=R0913
#                          Too many arguments

class Dependencies(JSONstruct):
    """the dependency database."""
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
            raise ValueError, "invalid max_state: %s" % max_state
        return set( [x for x in cls.states_list if cls.states_dict[x]<=idx])
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
    def __init__(self, dict_= None):
        """create the object."""
        super(Dependencies, self).__init__(dict_)
    def merge(self, other, constant_src_state= None):
        """merge another Dependencies object to self."""
        for modulename in other.iter_modulenames():
            m= self.datadict().setdefault(modulename,{})
            # iterate on stable, testing and unstable versions:
            for versionname in other.iter_versions(modulename, "unstable"):
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
                        vdict[dictname]= self.__class__._min_state(
                                (vdict[dictname], src_state))
                        # pylint: enable=W0212
                        continue
                    if dictname=="aliases":
                        try:
                            dict_update(vdict.setdefault(dictname,{}), 
                                        dictval)
                        except ValueError, e:
                            raise ValueError, \
                              "module %s version %s aliases: %s" % \
                              (modulename, versionname, str(e))
                        continue
                    if dictname=="source":
                        try:
                            dict_update(vdict, vdict2, [dictname])
                        except ValueError, e:
                            raise ValueError, \
                              "module %s version %s source: %s" % \
                              (modulename, versionname, str(e))
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
                    raise AssertionError, "unexpected dictname %s" % dictname
    def import_module(self, other, module_name, versionname):
        """copy the module data from another Dependencies object.

        This does a deepcopy of the data.
        """
        m= self.datadict().setdefault(module_name,{})
        m[versionname]= copy.deepcopy(
                            other.datadict()[module_name][versionname])
    def set_source(self, module_name, versionname, state, 
                   source_type, url, tag):
        """add a module with source specification."""
        if not self.__class__.states_dict.has_key(state):
            raise ValueError, "invalid state: %s" % state
        version_dict= self.datadict().setdefault(module_name,{})
        version= version_dict.setdefault(versionname, {})
        if not version.has_key("state"):
            version["state"]= state
        l= [source_type, url]
        if tag:
            l.append(tag)
        version["source"]= l
    def add_dependency(self, modulename, versionname, 
                       dep_modulename, dep_versionname, state):
        """add dependency for a module:version.
        """
        if not self.__class__.states_dict.has_key(state):
            raise ValueError, "invalid state: %s" % state
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
    def add_alias(self, modulename, versionname, 
                  alias_name, real_name):
        """add an alias for modulename:versionname."""
        m_dict= self.datadict()[modulename]
        alias_dict= m_dict[versionname].setdefault("aliases",{})
        if alias_dict.has_key(real_name):
            if alias_dict[real_name]==alias_name:
                return
            raise ValueError, \
                  "alias \"%s\" defined with two different names" % alias_name
        alias_dict[real_name]= alias_name
    def get_alias(self, modulename, versionname,
                  dep_modulename):
        """return the alias or the original name for dep_modulename."""
        a_dict= self.datadict()[modulename][versionname].get("aliases")
        if a_dict is None:
            return dep_modulename
        return a_dict.get(dep_modulename, dep_modulename)
    def assert_module(self, modulename, versionname):
        """do nothing if the module is found, raise KeyError otherwise.
        """
        d= self.datadict().get(modulename)
        if d is None:
            raise KeyError, "no data for module %s" % modulename
        v= d.get(versionname)
        if v is None:
            raise KeyError, "version %s not found for module %s" % \
                    (versionname, modulename)
    def dependencies_found(self, modulename, versionname):
        """returns True if dependencies are found for modulename:versionname.
        """
        # may raise KeyError exception in this line:
        d= self.datadict()[modulename][versionname]
        return d.has_key("dependencies")
    def module_source(self, modulename, versionname):
        """return a tuple (type,url,tag) for the module source."""
        l= self.datadict()[modulename][versionname]["source"]
        if len(l)<3:
            return (l[0], l[1], "")
        else:
            return tuple(l)
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
    def iter_dependency_versions(self, modulename, versionname,
                                 dependencyname, max_state):
        """return an iterator on dependency versions.
        
        max_state is the maximum allowed state:
          "stable"  : return just stable
          "testing" : return stable and testing
          "unstable": return stable, testing and unstable
        """
        # pylint: disable=W0212
        #                          Access to a protected member of a 
        #                          client class
        _states= self.__class__._allowed_states(max_state)
        # pylint: enable=W0212
        d= self.datadict()[modulename][versionname]
        deps= d.get("dependencies")
        if deps is None:
            raise StopIteration
        dep_dict= deps.get(dependencyname,{})
        if dep_dict is None:
            raise StopIteration
        for (dep_version, dep_state) in dep_dict.iteritems():
            if dep_state not in _states:
                continue
            yield dep_version
    def sorted_dependency_versions(self, modulename, versionname,
                                   dependencyname, max_state):
        """return sorted dependency versions.
        
        max_state is the maximum allowed state:
          "stable"  : return just stable
          "testing" : return stable and testing
          "unstable": return stable, testing and unstable
        """
        dep_list= list(self.iter_dependency_versions(modulename, versionname,
                                                     dependencyname, max_state))
        dep_list.sort(key= rev2key, reverse= True)
        return dep_list
    def iter_modulenames(self):
        """return an iterator on module names."""
        return self.datadict().iterkeys()
    def iter_versions(self, modulename, max_state):
        """return an iterator on versionnames of a module.
        
        max_state is the maximum allowed state:
          "stable"  : return just stable
          "testing" : return stable and testing
          "unstable": return stable, testing and unstable
        """
        # pylint: disable=W0212
        #                          Access to a protected member of a 
        #                          client class
        _states= self.__class__._allowed_states(max_state)
        # pylint: enable=W0212
        for versionname, versiondata in self.datadict()[modulename].iteritems():
            if versiondata["state"] not in _states:
                continue
            yield versionname
    def sorted_moduleversions(self, modulename, max_state):
        """return an iterator on sorted versionnames of a module."""
        return sorted(self.iter_versions(modulename, max_state),
                      key= rev2key,
                      reverse= True)
    def patch_version(self, modulename, versionname, newversionname,
                      do_replace):
        """add a new version to the database by copying the old one.

        do_replace: if True, replace the old version with the new one
        Note: the state of the new version is always set to unstable.
        """
        moduledata= self.datadict()[modulename]
        if moduledata.has_key(newversionname):
            raise ValueError, "module %s: version %s already exists" % \
                    (modulename, newversionname)
        d= copy.deepcopy(self.datadict()[modulename][versionname])
        src= d.get("source")
        if src:
            if len(src)>2: # a tag is defined
                src[2]= src[2].replace(versionname, newversionname)
        d["state"]= "unstable"
        moduledata[newversionname]= d
        if do_replace:
            del moduledata[versionname]
        # now scan all the references to modulename:versionname :
        for l_modulename in self.iter_modulenames():
            # scan stable, testing and unstable versions:
            for l_versionname in self.iter_versions(l_modulename, "unstable"):
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

    def partial_copy(self, elements):
        """take items from the Dependencies object and create a new one.
        
        elements must be a dict { modulename: versionname }. If versionname is
        None, take all versions of the module.

        Note that the new Dependencies object only contains references of the
        data. This DOES NOT do a deep copy.
        """
        new= self.__class__()
        for modulename, versionname in elements.items():
            d= new.datadict().setdefault(modulename, {})
            if versionname:
                versions= [versionname]
            else:
                # scan stable, testing and unstable versions:
                versions= self.iter_versions(modulename, "unstable")
            for version in versions:
                d[version]= self.datadict()[modulename][version]
        return new
    def partial_copy_by_specs(self, specs):
        """similar to partial_copy.

        specs is a list of strings of the form "modulename" or
        "modulename:versionname".
        """
        d= {}
        for s in specs:
            (modulename,flag,versionname)= scan_modulespec(s)
            if flag=="any":
                d[modulename]= None
            elif flag=="this":
                d[modulename]= versionname
            else:
                raise ValueError, "\"-version\" and \"+version\" not "+ \
                                  "supported here"
        return self.partial_copy(d)

# pylint: enable=R0904
# pylint: enable=R0913

# pylint: disable=R0904
#                          Too many public methods

class Builddb(JSONstruct):
    """the buildtree database."""
    states= set(("stable","testing","unstable"))
    @classmethod
    def guess_state(cls,st):
        """convert an abbreviation to a valid state."""
        errst= "error: cannot determine what state is meant by %s" % st
        match= guess_string(st, cls.states)
        if match is None:
            errst= "error: cannot determine what state is meant by %s" % st
            raise ValueError, errst
        return match
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
            raise ValueError, "not an allowed state: %s" % state
        d= self.datadict()
        if d.has_key(build_tag):
            raise ValueError, "cannot create, build %s already exists" % \
                               build_tag
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
            raise ValueError, "not an allowed state: %s" % new_state
        d= self.datadict()
        d[build_tag]["state"]= new_state
    def add_build(self, other, build_tag):
        """add build data from another Builddb to this one.

        Note: this does NOT do a deep copy, it copies just references.
        """
        d= self.datadict()
        if d.has_key(build_tag):
            raise ValueError, "cannot add, build %s already exists" % build_tag
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
    def filter_by_spec(self, string_specs):
        """return a new Builddb that satisfies the given list of specs.
        """
        specs= [scan_modulespec(s) for s in string_specs]
        new= self.__class__()
        for build_tag in self.iter_builds():
            found= True
            m= self.modules(build_tag)
            for (module,flag,version) in specs:
                v= m.get(module)
                if v is None:
                    found= False
                    break
                if not compare_versions_flag(flag,v,version):
                    found= False
                    break
            if found:
                new.add_build(self, build_tag)
        return new

    def iter_builds(self):
        """return a build iterator."""
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

# pylint: enable=R0904 

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
