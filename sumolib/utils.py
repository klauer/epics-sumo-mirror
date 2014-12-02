# pylint: disable=C0302
#                          Too many lines in module
"""Utilities for the SUMO scripts.
"""

# pylint: disable=C0322
#                          Operator not preceded by a space
# pylint: disable=C0103
#                          Invalid name for type variable
import sys
import os
import os.path
import re

__version__="2.2.3" #VERSION#

_pyver= (sys.version_info[0], sys.version_info[1])

if _pyver < (2,5):
    sys.exit("ERROR: SUMO requires at least Python 2.5, "
             "your version is %d.%d" % _pyver)

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
# user interaction
# -----------------------------------------------

def ask_yes_no(question, force_yes= None):
    """ask a yes or no question.

    returns:
      True  - if the user answered "yes" or "y"
      False - if the user answered "no" or "n"
    """
    if force_yes is not None:
        if force_yes:
            return True
    question+= " "
    while True:
        inp= raw_input(question).lower().strip()
        if inp in ["yes","y"]:
            return True
        if inp in ["no", "n"]:
            return False
        print "\tplease enter 'y', 'yes, 'n' or 'no'"
        question=""

def ask_abort(question, force_yes= None):
    """ask if the user wants to abort the program.

    Aborts the program if the user enters "y".
    """
    if force_yes is not None:
        if force_yes:
            return
    if not ask_yes_no(question + "Enter 'y' to continue or "
                                 "'n' to abort the program"):
        sys.exit("program aborted by user request")

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
# file utilities
# -----------------------------------------------

def file_w_open(filename, verbose, dry_run):
    """open a file for write."""
    if verbose:
        print "opening file '%s'" % filename
    if dry_run:
        return None
    return open(filename, "w")

def file_write(fh, st, verbose, dry_run):
    """write a line to a file."""
    if verbose:
        print st,
    if not dry_run:
        fh.write(st)

def mk_text_file(filename, lines, verbose, dry_run):
    """create a text file."""
    if verbose:
        if filename!="-":
            print "creating",filename
    if dry_run:
        filename="-"
    if filename=="-":
        fh= None
        # special settings for _fwrite:
        verbose= True
        dry_run= True
    else:
        fh= open(filename, "w")
    for l in lines:
        file_write(fh, l, verbose, dry_run)
    if filename!="-":
        fh.close()

# -----------------------------------------------
# directory utilities
# -----------------------------------------------

def changedir(newdir):
    """return the current dir and change to a new dir."""
    cwd= os.getcwd()
    os.chdir(newdir)
    return cwd

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

    This is needed to compare revision tags.

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

def is_standardpath(path, revision_tag):
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
    return tag2version(l[1])==tag2version(revision_tag)

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

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
