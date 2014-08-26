"""Lockfile support.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys

if __name__ == "__main__":
    # if this module is directly called like a script, we have to add the path
    # ".." to the python search path in order to find modules named
    # "sumo.[module]".
    sys.path.append("..")

import os
import sumo.system

__version__="1.8" #VERSION#

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
# ensure a certain module version
# -----------------------------------------------

def assert_version(wanted_version):
    """check if the version is the one that was expected."""
    if __version__!=wanted_version:
        sys.exit("ERROR: module 'sumo/locksupport' version %s expected "
                 "but found %s instead" % \
                 (wanted_version, __version__))

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
        sumo.system.system("%s %s" % (os.environ["VISUAL"], filename),
               False, False, verbose, dry_run)
    except IOError, _:
        sumo.system.system("%s %s" % (os.environ["EDITOR"], filename),
               False, False, verbose, dry_run)
    unlock_a_file(l)

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
