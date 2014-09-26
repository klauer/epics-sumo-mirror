"""JSON utilities.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import pprint
import os.path
import sumolib.lock

__version__="1.9" #VERSION#

assert __version__==sumolib.lock.__version__

_pyver= (sys.version_info[0], sys.version_info[1])

# -----------------------------------------------
# ensure a certain python version
# -----------------------------------------------

if _pyver < (2,5):
    sys.exit("ERROR: SUMO requires at least Python 2.5, "
             "your version is %d.%d" % _pyver)

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

def dump_file(filename, var):
    """Dump a variable to a file in JSON format.
    """
    fh= open(filename, "w")
    # modern python JSON modules add a trailing space at lines that end with a
    # comma. It seems that this is only fixed in python 3.4. So for now we
    # remove the spaces manually here, which is done by json_str().
    fh.write(json_str(var))
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
    <BLANKLINE>
    """
    if _JSON_TYPE==0:
        raw_str= json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        raw_str= json.dumps(var, sort_keys= True, indent= 4)

    # modern python JSON modules add a trailing space at lines that end
    # with a comma. It seems that this is only fixed in python 3.4. So for
    # now we remove the spaces manually here:

    lines= [x.rstrip() for x in raw_str.splitlines()]
    # effectively add a single newline at the end:
    lines.append("")
    return "\n".join(lines)

def dump(var):
    """Dump a variable in JSON format.

    Here is an example:
    >>> var= {"key":[1,2,3], "key2":"val", "key3":{"A":1,"B":2}}
    >>> dump(var)
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
    <BLANKLINE>
    """
    print json_str(var)

# pylint: enable=C0303
#                          Trailing whitespace

def json_load(data):
    """decode a JSON string.
    """
    return json.loads(data)

def loadfile(filename):
    """load a JSON file.

    If filename is "-" read from stdin.
    """
    if filename != "-":
        fh= open(filename)
    else:
        fh= sys.stdin

    # simplejson and json raise different kinds of exceptions
    # in case of a syntax error within the JSON file.
    if _JSON_TYPE==1:
        my_exceptionclass= ValueError
    else:
        my_exceptionclass= json.scanner.JSONDecodeError

    try:
        results= json.load(fh)
    except my_exceptionclass, e:
        if filename != "-":
            msg= "%s: %s" % (filename, str(e))
            fh.close()
        else:
            msg= "<stdin>: %s" % str(e)
        # always re-raise as a value error regardless of _JSON_TYPE:
        raise ValueError(msg)
    except IOError, e:
        if filename != "-":
            msg= "%s: %s" % (filename, str(e))
            fh.close()
        else:
            msg= "<stdin>: %s" % str(e)
        raise e.__class__(msg)
    if filename != "-":
        fh.close()
    return results

class Container(object):
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
        self.lock= sumolib.lock.lock_a_file(filename)
        self.lock_filename= filename
    def unlock_file(self):
        """remove a filelock if there is one."""
        if self.lock_filename is not None:
            sumolib.lock.unlock_a_file(self.lock)
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
            result= cls(loadfile(filename))
            result.selfcheck("(created from JSON string on stdin)")
            return result
        if not os.path.exists(filename):
            raise IOError("file \"%s\" not found" % filename)
        l= sumolib.lock.lock_a_file(filename)
        # If the line in "try" raises an exception, the file lock
        # is removed, then the exception is re-raised

        # simplejson and json raise different kinds of exceptions
        # in case of a syntax error within the JSON file.
        try:
            result= cls(loadfile(filename))
        except ValueError, _:
            sumolib.lock.unlock_a_file(l)
            raise

        if keep_locked:
            result.lock= l
            result.lock_filename= filename
        else:
            sumolib.lock.unlock_a_file(l)
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
            dump_file(filename, self.to_dict())
        if not dry_run:
            self.unlock_file()

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
