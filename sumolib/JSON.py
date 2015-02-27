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
import time
import sumolib.lock

__version__="2.6.2" #VERSION#

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
# -----------------------------------------------
# exceptions
# -----------------------------------------------

class ParseError(Exception):
    """This is raised when the JSON data is invalid."""
    pass

class InconsistentError(Exception):
    """This is raised when we cannot get consistent JSON data."""
    pass

# -----------------------------------------------
# JSON functions
# -----------------------------------------------

def dump_file(filename, var):
    """Dump a variable to a file in JSON format.

    This function uses a technique to write the file atomically. It assumes
    that we have a lock on the file so the temporary filename does not yet
    exist.
    """
    tmp_filename= "%s.tmp" % filename
    fh= open(tmp_filename, "w")
    # modern python JSON modules add a trailing space at lines that end with a
    # comma. It seems that this is only fixed in python 3.4. So for now we
    # remove the spaces manually here, which is done by json_str().
    fh.write(json_str(var))
    fh.flush()
    os.fsync(fh.fileno())
    fh.close()
    os.rename(tmp_filename, filename)

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
        raise ParseError(msg)
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
    def __init__(self, dict_= None, lock_timeout= None):
        """create the object."""
        if dict_ is None:
            self.dict_= {}
        else:
            self.dict_= dict_
        self.lock= None
        self._filename= None
        self._lock_timeout= lock_timeout
    def filename(self, new_name= None):
        """return or set the internal filename."""
        if new_name is None:
            return self._filename
        if new_name==self._filename:
            return
        # remove old locks that may exist:
        self.unlock_file()
        self._filename= new_name
    def dirname(self):
        """return the directory part of the internal filename."""
        return os.path.dirname(self._filename)
    def lock_file(self):
        """lock a file and store filename and lock in the object."""
        if not self._filename:
            raise ValueError("cannot lock JSON object: filename is not set")
        if self.lock:
            # already locked
            return
        lk= sumolib.lock.MyLock(self._filename, self._lock_timeout)
        # may raise lock.LockedError, lock.AccessError or OSError:
        lk.lock()
        self.lock= lk
    def unlock_file(self):
        """remove a filelock if there is one."""
        if self.lock:
            self.lock.unlock()
            self.lock= None
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
    def from_json_file(cls, filename,
                       keep_lock,
                       lock_timeout= None):
        """create an object from a json file.

        """
        # pylint: disable=R0912
        #                          Too many branches
        if not isinstance(keep_lock, bool):
            raise TypeError("wrong type of keep_lock")
        if filename=="-":
            result= cls(loadfile(filename))
            result.selfcheck("(created from JSON string on stdin)")
            return result
        if not os.path.exists(filename):
            raise IOError("file \"%s\" not found" % filename)
        l= sumolib.lock.MyLock(filename, lock_timeout)
        # may raise lock.LockedError, lock.AccessError or OSError:

        try:
            l.lock()
        except sumolib.lock.AccessError, _:
            if keep_lock:
                # we cannot keep the lock since we cannot create it, this is an
                # error:
                raise
            # we cannot create a lock but try to continue anyway:
            l= None

        if l is None:
            # We cannot create a file lock but be we try to read consistently:
            # it must be valid JSON and the file modification date must not
            # change.
            tmo= lock_timeout
            while True:
                t1= os.path.getmtime(filename)
                try:
                    data= loadfile(filename)
                except ParseError, _:
                    if tmo<=0:
                        raise
                    # if there is a timeout specified, try again:
                    tmo-=1
                    time.sleep(1)
                    continue
                t2= os.path.getmtime(filename)
                if t2!=t1:
                    # file modification time changed, we have to read again
                    # unless the time is expired:
                    if tmo<=0:
                        raise InconsistentError("File %s: cannot lock "
                                                "and cannot read "
                                                "consistently" % filename)
                    time.sleep(1)
                    tmo-=1
                    continue
                break
        else:
            try:
                # simplejson and json raise different kinds of exceptions
                # in case of a syntax error within the JSON file.
                data= loadfile(filename)
            except Exception, _:
                if l is not None:
                    l.unlock()
                raise

        result= cls(data, lock_timeout)

        if (not keep_lock) and (l is not None):
            l.unlock()
            l= None
        result.lock= l
        result.filename(filename)
        result.selfcheck("(created from JSON file %s)" % filename)
        return result
    def json_string(self):
        """return a JSON representation of the object."""
        return json_str(self.to_dict())
    def json_print(self):
        """print a JSON representation of the object."""
        print self.json_string()
    def json_save(self, filename, verbose, dry_run):
        """save as a JSON file.

        If filename is empty, use the default filename.

        Always remove a file lock if it existed before.
        """
        # pylint: disable=R0912
        #                          Too many branches
        if filename=="-":
            raise ValueError("filename must not be \"-\"")
        if filename:
            if self._filename!=filename:
                # remove a lock that may still exist:
                self.unlock_file()
            self._filename= filename
        backup= "%s.bak" % self._filename
        try:
            if not dry_run:
                self.lock_file()
            if os.path.exists(backup):
                if verbose:
                    print "remove %s" % backup
                if not dry_run:
                    os.remove(backup)
            if os.path.exists(self._filename):
                if verbose:
                    print "rename %s to %s" % (self._filename, backup)
                if not dry_run:
                    os.rename(self._filename, backup)
            if not dry_run:
                dump_file(self._filename, self.to_dict())
        finally:
            self.unlock_file()

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
