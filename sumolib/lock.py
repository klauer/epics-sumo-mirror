"""Lockfile support.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys
import os
import platform
import errno
import time

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumolib.[module]".
    sys.path.append("..")

import sumolib.system

__version__="2.6.2" #VERSION#

use_lockfile= True

try:
    import pwd
except ImportError:
    import getpass
    pwd = None

def current_user():
    """return the current user in a hopefully portable way."""
    if pwd:
        return pwd.getpwuid(os.geteuid()).pw_name
    else:
        return getpass.getuser()

# -----------------------------------------------
# exceptions
# -----------------------------------------------

class LockedError(Exception):
    """This is raised when we can't get a lock."""
    pass

class AccessError(Exception):
    """No rights to create a lock.

    This is raised when we can't create a lock due to access rights on the
    directory
    """
    pass

# -----------------------------------------------
# file locking wrapper
# -----------------------------------------------

# An extra locking mechanism (only for Linux) is implemented here in
# order to lock the file when the sumo-edit tool is used at the same
# time.

class MyLock(object):
    """Implement a simple file locking mechanism."""
    # pylint: disable=R0903
    #                          Too few public methods
    # pylint: disable=R0902
    #                          Too many instance attributes
    def _mkfile(self):
        """create a file, only for windows."""
        if self.method=="link":
            raise AssertionError("_mkfile should not be used for "
                                 "method 'link'")
    def lock(self):
        """do the file locking.

        raises:
          LockedError : can't get lock
          AccessError : no rights to create lock
          OSError     : other operating system errors

        On linux, create a symbolic link, otherwise a directory. The symbolic
        link has some information on the user, host and process ID.

        On other systems the created directory contains a file whose name has
        some information on the user, host and process ID.
        """
        if self.disabled:
            return
        if self.has_lock:
            raise AssertionError("cannot lock '%s' twice" % self.filename)
        self.info="%s@%s:%s" % (current_user(),
                                platform.node(),
                                os.getpid())
        tmo= self.timeout
        while True:
            try:
                if self.method=="link":
                    os.symlink(self.info, self.lockname)
                else:
                    os.mkdir(self.lockname)
                    open(os.path.join(self.lockname,self.info),'w').close()
            except OSError, e:
                # probably "File exists"
                if e.errno==errno.EEXIST:
                    if tmo>0:
                        tmo-= 1
                        time.sleep(1)
                        continue
                    if self.method=="link":
                        raise LockedError("file '%s' is locked: %s" % \
                                      (self.filename,
                                       os.readlink(self.lockname)))
                    else:
                        txt= " ".join(os.listdir(self.lockname))
                        raise LockedError("file '%s' is locked: %s" % \
                                      (self.filename, txt))
                elif e.errno==errno.EACCES:
                    # cannot write to directory
                    raise AccessError(("no rights to create lock for "
                                       "file '%s'") % self.filename)
                else:
                    # re-raise exception in all other cases
                    raise
            break
        self.has_lock= True
    def __init__(self, filename, timeout= None):
        """create a portable lock.

        If timeout is a number, wait up to this time (seconds) to aquire the
        lock.
        """
        if not use_lockfile:
            self.disabled= True
        else:
            self.disabled= False
        if timeout is None:
            self.timeout= 0
        else:
            if not isinstance(timeout, int):
                raise TypeError("timeout must be None or an int")
            if timeout<0:
                raise ValueError("timeout must be >=0")
            self.timeout= timeout

        self.filename= filename
        self.lockname= "%s.lock" % self.filename
        self.has_lock= False
        self.info= None
        if platform.system()=="Linux":
            self.method= "link"
        else:
            self.method= "mkdir"
    def unlock(self, force= False):
        """unlock."""
        if self.disabled:
            return
        if not force:
            if not self.has_lock:
                raise AssertionError("cannot unlock since a lock "
                                     "wasn't taken")
        if self.method=="link":
            os.unlink(self.lockname)
        else:
            for f in os.listdir(self.lockname):
                os.unlink(os.path.join(self.lockname,f))
            os.rmdir(self.lockname)
        self.has_lock= False

# -----------------------------------------------
# edit with lock:
# -----------------------------------------------

def edit_with_lock(filename, verbose, dry_run):
    """lock a file, edit it, then unlock the file."""
    if not os.path.exists(filename):
        raise IOError("error: file \"%s\" doesn't exist" % filename)
    envs=["VISUAL","EDITOR"]
    ed_lst= [v for v in [os.environ.get(x) for x in envs] if v is not None]
    if not ed_lst:
        raise IOError("error: environment variable 'VISUAL' or "
                      "'EDITOR' must be defined")
    mylock= MyLock(filename)
    mylock.lock()
    try:
        found= False
        errors= ["couldn't start editor(s):"]
        for editor in ed_lst:
            try:
                sumolib.system.system("%s %s" % (editor, filename),
                                      False, False, verbose, dry_run)
                found= True
                break
            except IOError, e:
                # cannot find or not start editor
                errors.append(str(e))
    finally:
        mylock.unlock()
    if not found:
        raise IOError("\n".join(errors))

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
