"""Repository support
"""

# pylint: disable=C0103
#                          Invalid name for type variable
import os.path
import sys

import sumolib.utils
import sumolib.lock
import sumolib.JSON
import sumolib.patch
import sumolib.path
import sumolib.tar
import sumolib.darcs
import sumolib.mercurial # "hg"
import sumolib.git

__version__="2.8" #VERSION#

assert __version__==sumolib.utils.__version__
assert __version__==sumolib.lock.__version__
assert __version__==sumolib.JSON.__version__
assert __version__==sumolib.patch.__version__
assert __version__==sumolib.path.__version__
assert __version__==sumolib.tar.__version__
assert __version__==sumolib.darcs.__version__
assert __version__==sumolib.mercurial.__version__
assert __version__==sumolib.git.__version__

known_repos=set(("darcs","hg","git"))
known_no_repos= set(("path","tar"))
known_sources= set(known_no_repos).union(known_repos)

# ---------------------------------------------------------
# scan a directory:

def repo_from_dir(directory, hints, verbose, dry_run):
    """scan a directory and return a repository object.

    Hints must be a dictionary. This gives hints how the directory should be
    scanned. Currently we know these keys in the dictionary:

    "ignore changes": sumolib.utils.RegexpMatcher
        All local changes in files that match the RegexpMatcher object are
        ignored. By this we can get the remote repository and tag from a
        directory although there are uncomitted changes. A common application
        is to ignore changes in file "configure/RELEASE".
    "dir patcher": sumolib.utils.RegexpPatcher
        This patcher is applied to the directory that is stored in the object.
    "url patcher": sumolib.utils.RegexpPatcher
        This patcher is applied to the URL that is stored in the object.
    "force local": bool
        If this is True, the returned repository object does not contain a
        remote repository url even if there was one.
    "write check": bool
        If this is True, when the repository data directory is not writable
        the function returns <None>.
    """
    if not isinstance(hints, dict):
        raise TypeError("hints parameter '%s' is of wrong type" % \
                        repr(hints))
    obj= sumolib.darcs.Repo.scan_dir(directory, hints, verbose, dry_run)
    if obj is not None:
        return obj
    obj= sumolib.mercurial.Repo.scan_dir(directory, hints, verbose, dry_run)
    if obj is not None:
        return obj
    obj= sumolib.git.Repo.scan_dir(directory, hints, verbose, dry_run)
    if obj is not None:
        return obj
    return

def src_from_dir(directory, hints, verbose, dry_run):
    """scan a directory and return a repository object.

    Hints must be a dictionary. This gives hints how the directory should be
    scanned. Currently we know these keys in the dictionary:

    "ignore changes": sumolib.utils.RegexpMatcher
        All local changes in files that match the RegexpMatcher object are
        ignored. By this we can get the remote repository and tag from a
        directory although there are uncomitted changes. A common application
        is to ignore changes in file "configure/RELEASE".
    "dir patcher": sumolib.utils.RegexpPatcher
        This patcher is applied to the directory that is stored in the object.
    "url patcher": sumolib.utils.RegexpPatcher
        This patcher is applied to the URL that is stored in the object.
    "force path" : bool
        If this is True, a Path object is always returned, even if a repository
        was found.
    """
    if not isinstance(hints, dict):
        raise TypeError("hints parameter '%s' is of wrong type" % \
                        repr(hints))
    if hints.get("force path"):
        return sumolib.path.Repo.scan_dir(directory, hints, verbose, dry_run)

    obj= sumolib.tar.Repo.scan_dir(directory, hints, verbose, dry_run)
    if obj is not None:
        return obj
    # insert other repo supports here
    return sumolib.path.Repo.scan_dir(directory, hints, verbose, dry_run)

# ---------------------------------------------------------
# check out:

def checkout(sourcespec, destdir, verbose, dry_run):
    """check out a working copy.

    sourcespec must be a SourceSpec object.
    """
    # pylint: disable=R0913
    #                          Too many arguments
    if not isinstance(sourcespec, SourceSpec):
        raise TypeError("error, '%s' is not of type SourceSpec" % \
                        repr(sourcespec))
    repotype= sourcespec.sourcetype()
    spec= sourcespec.spec_val()
    if repotype == "darcs":
        sumolib.darcs.Repo.checkout(spec, destdir, verbose, dry_run)
    elif repotype == "hg":
        sumolib.mercurial.Repo.checkout(spec, destdir, verbose, dry_run)
    elif repotype == "git":
        sumolib.git.Repo.checkout(spec, destdir, verbose, dry_run)
    elif repotype== "tar":
        sumolib.tar.Repo.checkout(spec, destdir, verbose, dry_run)
    elif repotype== "path":
        sumolib.path.Repo.checkout(spec, destdir, verbose, dry_run)
    else:
        raise ValueError("unsupported repotype: %s" % repotype)
    p= sourcespec.patches()
    if p:
        sumolib.patch.apply_patches(destdir, p, verbose, dry_run)


# ---------------------------------------------------------
# SourceSpec class:

class SourceSpec(sumolib.JSON.Container):
    """hold the source specification.
    """
    # pylint: disable=R0904
    #                          Too many public methods
    def __init__(self, dict_= None):
        """create the object."""
        super(SourceSpec, self).__init__(dict_)
    # pylint: disable=C0301
    #                          Line too long
    @classmethod
    def from_string_sourcespec(cls, elms):
        """scan a source specification.

        A sourcespec is a list of strings. Currently we support here:
        ["path",PATH] or ["tar",TARFILE,{PATCHFILES}] or
        [<repotype>,URL] or [<repotype>,URL,TAG,{PATCHFILES}]

        where <repotype> may be one of the strings in
        sumolib.repos.known_repos

        Here are some examples:

        >>> SourceSpec.from_string_sourcespec(["path","ab"])
        SourceSpec({'path': 'ab'})
        >>> SourceSpec.from_string_sourcespec(["path"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec 'path'
        >>> SourceSpec.from_string_sourcespec(["path","a","b"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec 'path a b'
        >>> SourceSpec.from_string_sourcespec(["darcs","abc"])
        SourceSpec({'darcs': {'url': 'abc'}})
        >>> SourceSpec.from_string_sourcespec(["darcs","abc","R1-2"])
        SourceSpec({'darcs': {'url': 'abc', 'tag': 'R1-2'}})
        >>> SourceSpec.from_string_sourcespec(["darcs"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec 'darcs'
        >>> SourceSpec.from_string_sourcespec(["darcs","abc","R1-2","xy"])
        SourceSpec({'darcs': {'url': 'abc', 'tag': 'R1-2', 'patches': ['xy']}})
        >>> SourceSpec.from_string_sourcespec(["darcs","abc","R1-2","xy","z"])
        SourceSpec({'darcs': {'url': 'abc', 'tag': 'R1-2', 'patches': ['xy', 'z']}})
        """
        if elms[0] not in known_sources:
            raise ValueError("unknown source type '%s'" % elms[0])
        if len(elms)<2:
            raise ValueError("invalid source spec '%s'" % (" ".join(elms)))
        if elms[0]=="path":
            if len(elms)!=2:
                raise ValueError("invalid source spec '%s'" % (" ".join(elms)))
            return cls({elms[0]: elms[1]})
        if elms[0]=="tar":
            if len(elms)<2:
                raise ValueError("invalid source spec '%s'" % (" ".join(elms)))
            d= { "url": elms[1] }
            if len(elms)>2:
                d["patches"]= elms[2:]
            return cls({elms[0]: d})
        d= { "url": elms[1] }
        if len(elms)>2:
            d["tag"]= elms[2]
        if len(elms)>3:
            d["patches"]= elms[3:]
        return cls({elms[0]: d})
    # pylint: enable=C0301
    #                          Line too long
    def sourcetype(self):
        """return the type of the source."""
        d= self.datadict()
        return sumolib.utils.single_key(d)
    def is_repo(self):
        """return if SourceSpec refers to a repository.
        """
        return self.sourcetype() in known_repos
    def path(self, new_val= None):
        """return the path if the type is "path"."""
        (d, type_, pars)= self._unpack()
        if type_!= "path":
            raise TypeError("error, 'path()' can only be called for "
                            "SourceSpec objects of type 'path'")
        if new_val is None:
            return pars
        d[type_]= new_val
    def tag(self, new_val= None):
        """return the tag if it exists."""
        (_, type_, pars)= self._unpack()
        if not isinstance(pars, dict):
            if new_val is not None:
                raise ValueError("error, cannot set tag on type %s" % type_)
            return
        if new_val is None:
            return pars.get("tag")
        pars["tag"]= new_val
    def url(self, new_val= None):
        """return the url if it exists."""
        (_, type_, pars)= self._unpack()
        if not isinstance(pars, dict):
            if new_val is not None:
                raise ValueError("error, cannot set url on type %s" % type_)
            return
        if new_val is None:
            return pars.get("url")
        pars["url"]= new_val
    def patches(self, new_val= None):
        """return the patches if they exist."""
        (_, type_, pars)= self._unpack()
        if not isinstance(pars, dict):
            if new_val is not None:
                raise ValueError("error, cannot set patches on type %s" % type_)
            return
        if new_val is None:
            return pars.get("patches")
        pars["patches"]= new_val
    def spec_val(self):
        """return the *value* of the source specification.

        As SourceSpec is currently used this can be a string (type "path") or a
        dict (all other types).
        """
        (_, _, pars)= self._unpack()
        return pars
    def _unpack(self):
        """return the internal dict, the sourcetype and the parameters.
        """
        d= self.datadict()
        type_= sumolib.utils.single_key(d)
        return (d, type_, d[type_])
    def copy_spec(self, other):
        """simply overwrite self with other."""
        (self_d, self_type, _)= self._unpack()
        # pylint: disable=W0212
        #                          Access to a protected member
        (_, other_type, other_pars)= other._unpack()
        del self_d[self_type]
        # reconstruct other_pars if it is an object. For dicts this creates a
        # second independent dict:
        self_d[other_type]= other_pars.__class__(other_pars)
    def change_source(self, other):
        """set source spec by copying information from another object.

        This can also handle wildcards.

        returns True if the spec was changed, False if it wasn't.
        """
        (self_d, self_type, self_pars)   = self._unpack()
        # pylint: disable=W0212
        #                          Access to a protected member
        (_, other_type, other_pars)= other._unpack()

        if self_type!=other_type:
            self.copy_spec(other)
            return True

        if isinstance(other_pars, basestring):
            # this is only the case for type "path":
            if other_pars=="*" or other_pars==".":
                # no changes
                return False
            self_d[self_type]= other_pars
            return True
        if isinstance(other_pars, dict):
            # tar file or a repository type
            original= dict(self_pars)
            self_pars.clear()
            for (k,v) in other_pars.items():
                if v=="*" or v==".":
                    v= original.get(k)
                    if v is None:
                        raise ValueError("cannot replace wildcard "
                                         "for key %s" % k)
                self_pars[k]= v
            # return whether there were changes:
            return self_pars!=original
        else:
            raise AssertionError("unexpected type: %s" % repr(other_pars))
    def change_source_by_tag(self, tag):
        """change the source spec just by providing a tag.

        returns True if the spec was changed, False if it wasn't.
        """
        (_, self_type, self_pars)   = self._unpack()
        if self_type in known_no_repos:
            raise ValueError("you cannot provide just a new tag for "
                             "a source specification of "
                             "type '%s'" % self_type)
        old= self_pars.get("tag")
        if old==tag:
            return False
        self_pars["tag"]= tag
        return True

# ---------------------------------------------------------
# ManagedRepo class

class ManagedRepo(object):
    """Object for managing data in a repository.

    Do pull before read,
    commit and push after write.
    """
    # pylint: disable=R0902
    #                          Too many instance attributes
    def __init__(self, sourcespec,
                 mode, directory,
                 lock_timeout,
                 verbose, dry_run):
        """create the object.

        sourcespec must be a SourceSpec object or <None>.

        spec must be a dictionary with "url" and "tag" (optional).

        mode must be "get", "pull" or "push".
          get: only create the repo if it doesn't yet exist, nothing else
          pull: pull and merge before every read
          push: like pull but push after every write

        If sourcespec is None, create an empty object that basically
        does nothing.

        Does checkout the repository if the directory does not yet exist.
        """
        # pylint: disable=R0913
        #                          Too many arguments
        # pylint: disable=R0912
        #                          Too many branches
        self.sourcespec= sourcespec
        if sourcespec is None:
            return

        if not isinstance(sourcespec, SourceSpec):
            raise TypeError("error, '%s' is not of type SourceSpec" % \
                            repr(sourcespec))

        if mode not in ["get","pull","push"]:
            raise AssertionError("unknown mode: %s" % repr(mode))
        self.lock_timeout= lock_timeout
        self.mode= mode
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        # lockfile will be named "repo.lock":
        lockname= os.path.join(self.directory, "repo")
        self.lock= sumolib.lock.MyLock(lockname, self.lock_timeout)

        if not os.path.exists(self.directory):
            # must create
            # first get a lock for the directory to create:
            lk= sumolib.lock.MyLock(self.directory, self.lock_timeout)
            try:
                lk.lock()
            except sumolib.lock.AccessError, _:
                # we cannot write although we have to check out
                raise OSError("Error, cannot write to directory %s" % \
                              os.path.dirname(self.directory))
            # sumolib.lock.LockedError is not caught here

            # the directory may have been created in the meantime by another
            # process:
            if not os.path.exists(self.directory):
                # must check out
                try:
                    checkout(self.sourcespec, self.directory,
                             self.verbose, self.dry_run)
                except Exception, _:
                    lk.unlock()
                    raise
                if not os.path.exists(self.directory):
                    lk.unlock()
                    raise AssertionError("checkout of %s to %s failed" % \
                                         (self.sourcespec,
                                          self.directory))
            lk.unlock()
        if not os.path.isdir(self.directory):
            raise AssertionError("error, '%s' is not a directory" % \
                                 self.directory)

        no_write_access= False
        # get a repository lock:
        try:
            self.lock.lock()
        except sumolib.lock.AccessError, _:
            # we do not have write access on the repository:
            no_write_access= True

        if no_write_access:
            # basically disable all action on the repository:
            # Setting self.sourcespec to <None> basically disables the
            # ManagedRepo object.
            if self.mode!='get':
                sys.stderr.write("warning: no write access to dependency "
                                 "database, forcing dbrepomode 'get'\n")
            self.sourcespec= None
            return

        self.repo_obj= None
        try:
            self.repo_obj= repo_from_dir(self.directory,
                                         {"write check": True},
                                         self.verbose, self.dry_run)
        finally:
            self.lock.unlock()

        if self.repo_obj is None:
            # basically disable all action on the repository:
            # Setting self.sourcespec to <None> basically disables the
            # ManagedRepo object.
            self.sourcespec= None

    def local_changes(self):
        """return if there are local changes."""
        if self.sourcespec is None:
            # for the "empty" ManagedRepo object just return <None>:
            return
        return self.repo_obj.local_changes
    def commit(self, message):
        """commit changes."""
        self.lock.lock()
        try:
            self.repo_obj.commit(message)
        finally:
            self.lock.unlock()
    def prepare_read(self):
        """do checkout or pull."""
        if self.sourcespec is None:
            return
        # pylint: disable=E1103
        #                          Instance of 'Repo' has no 'pull' member
        if self.mode!='get':
            self.lock.lock()
            try:
                self.repo_obj.pull_merge()
            finally:
                self.lock.unlock()
    def finish_write(self, message):
        """do commit and push."""
        if self.sourcespec is None:
            return
        if not self.repo_obj:
            raise AssertionError("internal error, repo obj missing")
        # pylint: disable=E1103
        #                          Instance of 'Repo' has no '...' member
        self.lock.lock()
        try:
            self.repo_obj.commit(message)
            if self.mode=='push':
                self.repo_obj.push()
        finally:
            self.lock.unlock()

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
