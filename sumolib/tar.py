"""tar file support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os.path
import shutil
import sumolib.system
import sumolib.utils

__version__="2.3.1" #VERSION#

assert __version__==sumolib.system.__version__
assert __version__==sumolib.utils.__version__

# -----------------------------------------------
# Repo class
# -----------------------------------------------

class Repo(object):
    """represent a tar."""
    def _hint(self, name):
        """return the value of hint "name"."""
        return self.hints.get(name)
    @staticmethod
    def _find_tar(directory):
        """look for a tar file for <directory>.

        If directory is "a/b/c" look for:
          a/b/c.tar
          a/b/c.tar.gz
          a/b/c.tar.bz
          a/b-c.tar
          a/b-c.tar.gz
          a/b-c.tar.bz
        """
        def find(directory):
            """try to find the tar file."""
            for ext in [".tar",".tar.gz",".tar.bz"]:
                f= directory+ext
                if os.path.exists(f):
                    return f
            return
        abs_directory= os.path.abspath(directory)
        (d,base)= os.path.split(abs_directory)
        (dir_,parent)= os.path.split(d)
        paths= [abs_directory,
                os.path.join(dir_,"%s-%s" % (parent,base)),
               ]
        for p in paths:
            result= find(p)
            if result is not None:
                return result
        return
    def __init__(self, directory, tar_file, hints, verbose, dry_run):
        """initialize."""
        # pylint: disable=R0913
        #                          Too many arguments
        self.hints= dict(hints) # shallow copy
        patcher= self._hint("dir patcher")
        if patcher is not None:
            directory= patcher.apply(directory)
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        self.tar_file= tar_file
    def __str__(self):
        """return a human readable representation."""
        lines= [ "tar file",
                 "dir: %s" % repr(self.directory),
                 "tar file: %s" % repr(self.tar_file)
               ]
        return "\n".join(lines)
    def name(self):
        """return the repo type name."""
        # pylint: disable=R0201
        #                          Method could be a function
        return "tar"
    @classmethod
    def scan_dir(cls, directory, hints, verbose, dry_run):
        """return a Repo object."""
        # pylint: disable=W0613
        #                          Unused argument
        tar_file= None
        # If directory is None we want to create an "empty" object
        # intentionally. In this case we don't look for a tar file.
        # If directory is given however, we must find a tar file. If we don't
        # we return <None>.
        if directory is not None:
            tar_file= cls._find_tar(directory)
            if tar_file is None:
                return
        return cls(directory, tar_file, hints, verbose, dry_run)
    def source_spec(self, patcher= None):
        """return a complete source specification (for SourceSpec class).
        """
        def p(st):
            """apply patcher if it is given."""
            if patcher is None:
                return st
            return patcher.apply(st)
        if self.directory is None:
            raise AssertionError("cannot create source_spec from "
                                 "empty object")
        d= {"tar": p(self.tar_file)}
        return d
    @staticmethod
    def checkout(spec, destdir, verbose, dry_run):
        """spec must be a string.
        """
        # pylint: disable=R0914
        #                          Too many local variables
        p_basename= os.path.basename
        p_dirname = os.path.dirname
        p_dirjoin = os.path.join
        p_abspath = os.path.abspath
        p_isdir =   os.path.isdir
        def only_dir(dir_):
            """If dir_ has a single subdir, return it."""
            contents= os.listdir(dir_)
            if len(contents)!=1:
                return
            subdir= p_dirjoin(dir_,contents[0])
            if p_isdir(subdir):
                return subdir
            return

        if not isinstance(spec, basestring):
            raise TypeError("spec '%s' must be a string here" % repr(spec))
        ap_spec= p_abspath(spec)
        ext= os.path.splitext(spec)[1]
        if ext==".tar":
            tar_args= "-xf"
        elif ext==".gz":
            tar_args= "-xzf"
        elif ext==".bz2":
            tar_args= "-xjf"
        else:
            raise ValueError("unknown file %s extension at %s" % (ext,spec))
        ap_destdir= p_abspath(destdir)
        ap_tempdir= destdir+".tmp"
        os.makedirs(ap_tempdir)
        cwd= sumolib.utils.changedir(ap_tempdir)
        try:
            sumolib.system.system("tar %s %s" % (tar_args, ap_spec),
                               False, False, verbose, dry_run)
        finally:
            sumolib.utils.changedir(cwd)
        ap_subdir= only_dir(ap_tempdir)
        if not ap_subdir:
            os.rename(ap_tempdir, ap_destdir)
            return
        # if the tar file created a single directory within ap_tempdir we have
        # to remove one directory hierarchy:
        ap_renamed_subdir= p_dirjoin(ap_tempdir, p_basename(destdir))
        os.rename(ap_subdir, ap_renamed_subdir)
        shutil.move(ap_renamed_subdir, p_dirname(ap_tempdir))
        os.rmdir(ap_tempdir)


