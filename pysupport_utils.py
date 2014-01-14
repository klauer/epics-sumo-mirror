"""Utilities for the pysupport scripts.
"""
import sys
import subprocess
import os.path

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
    if _JSON_TYPE==0:
        print json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        print json.dumps(var, sort_keys= True, indent= 4)

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
    """add a key, create a list if needed.

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

def split_version(path):
    """split a path into (base, version).

    A path may have two forms:

      a/b/c/version       - splitted to "a/b/c" and "version"
      darcs,a/b/c,version - splitted to "darcs,a/b/c" and "version"
    """
    l= path.split(",")
    if len(l)==3:
        return (",".join(l[0:2]),l[2])
    return os.path.split(path)

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

def uni_path(parts, tag_required= False):
    """create a universal path.

    parts must be a list. If it is only one element, the function returns
    "path,<parts>". If it has more than one element, the function returns a
    string that is a comma separated list of the parts.

    The concept here is to identify paths, repoisitories and repositories with
    a tag with a string. We currently have three possibilities:

      path,<path>                 - a simple path
      darcs,<repo-url>            - a darcs repository
      darcs,<repo-url>,<repo-tag> - a darcs repository with a tag
    """
    if len(parts)==1:
        return "path,%s" % parts[0]
    return ",".join(parts)

def is_standardpath(path, darcs_tag):
    """checks if path is complient to Bessy convention for support paths.
    
    Here are some examples:
    >>> is_standardpath("support/mcan/2-3", "R2-3")
    True
    >>> is_standardpath("support/mcan/2-3", "R2-4")
    False
    >>> is_standardpath("support/mcan/head", "R2-3")
    False
    """
    l= split_version(path)
    if len(l)<2:
        return False
    return l[1]==tag2version(darcs_tag)


def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
