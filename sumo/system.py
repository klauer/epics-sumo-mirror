"""System utilities.
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import sys
import subprocess

__version__="1.8" #VERSION#

# -----------------------------------------------
# ensure a certain module version
# -----------------------------------------------

def assert_version(wanted_version):
    """check if the version is the one that was expected."""
    if __version__!=wanted_version:
        sys.exit("ERROR: module 'sumo/systemsupport' version %s expected "
                 "but found %s instead" % \
                 (wanted_version, __version__))

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
            return (None, None)
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

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
