"""Utilities for the pysupport scripts.
"""
import sys
import subprocess
import os.path
import pprint

# pylint: disable=C0322,C0103

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
    """Dump a variable in JSON format to a file.

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
    # pylint: disable= E1101
    if p.returncode!=0:
        raise IOError(p.returncode,
                      "cmd \"%s\", errmsg \"%s\"" % (cmd,child_stderr))
    # pylint: enable= E1101
    return(child_stdout)

# -----------------------------------------------
# version and path support
# -----------------------------------------------

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
    """convert a revsion number to a comparable string.

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
        if len(rev)<=1:
            return "-"
        rev= rev[1:]
    if len(rev)>1:
        if rev[0]=="R" and rev[1].isdigit():
            rev= rev[1:]
    if not rev[0].isdigit():
        return "-"+rev
    rev= rev.replace("-",".")
    l= rev.split(".")
    n= []
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
    return l[1]==tag2version(darcs_tag)

class Builddb(object):
    """the buildtree database."""
    def __init__(self, dict_= None):
        """create the object."""
        if dict_ is None:
            self.dict_= {}
        else:
            self.dict_= dict_
    def add(self, other):
        """add data from another Builddb object."""
        for key in ["modules", "linked"]:
            self.dict_[key].update(other[key])
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
    def from_json_file(cls, filename):
        """create an object from a json file."""
        if os.path.exists(filename):
            return cls(json_loadfile(filename))
        else:
            return cls()
    def add_json_file(self, filename):
        """add data from a JSON file."""
        data= json_loadfile(filename)
        self.add(data)
    def json_string(self):
        """return a JSON representation of the object."""
        return json_str(self.to_dict())
    def json_print(self):
        """print a JSON representation of the object."""
        print self.json_string()
    def json_save(self, filename, verbose, dry_run):
        """save as a JSON file."""
        backup= "%s.bak" % filename
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
    def has_build_tag(self, build_tag):
        """returns if build_tag is contained."""
        return self.dict_.has_key(build_tag)
    def add_module(self, build_tag, 
                   module_build_tag,
                   modulename, versionname):
        """add a module definition."""
        build_= self.dict_.setdefault(build_tag, {})
        modules_= build_.setdefault("modules", {})
        modules_[modulename]= versionname
        if build_tag!= module_build_tag:
            linked_ = build_.setdefault("linked", {})
            linked_[modulename]= module_build_tag
    def has_module(self, build_tag, modulename):
        """returns if the module is contained here."""
        build_= self.dict_[build_tag]
        module_dict= build_["modules"]
        return module_dict.has_key(modulename)

    def module_is_linked(self, build_tag, 
                         modulename):
        """return if the module is linked."""
        build_= self.dict_[build_tag]
        linked_ = build_.get("linked")
        if linked_ is None:
            return False
        return linked_.has_key(modulename)
    def iter_builds(self):
        """return a build iterator."""
        for t in sorted(self.dict_.keys()):
            yield t
    def iter_modules(self, build_tag):
        """return an iterator on the modules."""
        build_= self.dict_[build_tag]
        module_dict= build_["modules"]
        for module in sorted(module_dict.keys()):
            yield (module, module_dict[module])
    def modules(self, build_tag):
        """return all modules of a build."""
        build_ = self.dict_[build_tag]
        return build_["modules"]

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
