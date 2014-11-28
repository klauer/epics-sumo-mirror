"""Repository support
"""

# pylint: disable=C0103
#                          Invalid name for type variable
import os.path

import sumolib.utils
import sumolib.path
import sumolib.tar
import sumolib.darcs
import sumolib.mercurial # "hg"
import sumolib.git

__version__="2.2" #VERSION#

assert __version__==sumolib.utils.__version__
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

def checkout(repotype, spec, destdir, verbose, dry_run):
    """check out a working copy.

    spec must be a dictionary with "url" and "tag" (optional).
    """
    # pylint: disable=R0913
    #                          Too many arguments
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
    @classmethod
    def from_param(cls, sourcetype, url=None, tag=None,
                   rev=None, tar=None, path=None):
        """create by parameters.
        """
        # pylint: disable=R0912
        #                          Too many branches
        # pylint: disable=R0913
        #                          Too many arguments
        if sourcetype not in known_sources:
            raise ValueError("unknown source type: '%s'" % sourcetype)
        if sourcetype=="path":
            if not path:
                raise ValueError("'path' missing for sourcetype 'path'")
            return cls({"path": path})
        if sourcetype=="tar":
            if not tar:
                raise ValueError("'tar' missing for sourcetype 'tar'")
            return cls({"tar": tar})
        if sourcetype=="darcs":
            if not url:
                raise ValueError("'url' missing for sourcetype 'darcs'")
            d= {"url": url}
            if tag:
                d["tag"]= tag
            return cls({sourcetype: d})
        if sourcetype=="hg":
            if not url:
                raise ValueError("'url' missing for sourcetype 'hg'")
            d= {"url": url}
            if tag and rev:
                raise ValueError("you cannot specify tag AND revision")
            if tag:
                d["tag"]= tag
            if rev:
                d["rev"]= rev
            return cls({sourcetype: d})
        if sourcetype=="git":
            if not url:
                raise ValueError("'url' missing for sourcetype 'git'")
            d= {"url": url}
            if tag and rev:
                raise ValueError("you cannot specify tag AND revision")
            if tag:
                d["tag"]= tag
            if rev:
                d["rev"]= rev
            return cls({sourcetype: d})
        raise AssertionError("unknown sourcetype: %s" % sourcetype)
    @classmethod
    def from_string_sourcespec(cls, elms):
        """scan a source specification.

        A sourcespec is a list of strings. Currently we support here:
        ["path",PATH] or ["tar",TARFILE] or
        [<repotype>,URL] or [<repotype>,URL,TAG].

        where <repotype> may be one of the strings in
        sumolib.repos.known_repos

        Here are some examples:

        >>> SourceSpec.from_string_sourcespec(["path","ab"])
        SourceSpec({'path': 'ab'})
        >>> SourceSpec.from_string_sourcespec(["path"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec: 'path'
        >>> SourceSpec.from_string_sourcespec(["path","a","b"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec: 'path a b'
        >>> SourceSpec.from_string_sourcespec(["darcs","abc"])
        SourceSpec({'darcs': {'url': 'abc'}})
        >>> SourceSpec.from_string_sourcespec(["darcs","abc","R1-2"])
        SourceSpec({'darcs': {'url': 'abc', 'tag': 'R1-2'}})
        >>> SourceSpec.from_string_sourcespec(["darcs"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec: 'darcs'
        >>> SourceSpec.from_string_sourcespec(["darcs","abc","R1-2","xy"])
        Traceback (most recent call last):
            ...
        ValueError: invalid source spec: 'darcs abc R1-2 xy'
        """
        if elms[0] not in known_sources:
            raise ValueError("unknown source type: '%s'" % elms[0])
        if elms[0]=="path" or elms[0]=="tar":
            if len(elms)!=2:
                raise ValueError("invalid source spec: '%s'" % (" ".join(elms)))
            return cls({elms[0]: elms[1]})
        if len(elms)==2:
            return cls({elms[0]:{"url":elms[1]}})
        elif len(elms)==3:
            return cls({elms[0]:{"url":elms[1], "tag":elms[2]}})
        else:
            raise ValueError("invalid source spec: '%s'" % (" ".join(elms)))
    def sourcetype(self):
        """return the type of the source."""
        d= self.datadict()
        return sumolib.utils.single_key(d)
    def is_repo(self):
        """return if SourceSpec refers to a repository.
        """
        return self.sourcetype() in known_repos
    @staticmethod
    def _set_get(dict_, name, new_val= None):
        """get or set a property."""
        if new_val is None:
            return dict_.get(name)
        dict_[name]= new_val
        return new_val
    def tag(self, new_val= None):
        """return the tag."""
        (_, _, pars)= self.unpack()
        # pylint: disable=W0212
        #                          Access to protected member
        return self.__class__._set_get(pars, "tag", new_val)
    def rev(self, new_val= None):
        """return the revision number."""
        (_, _, pars)= self.unpack()
        # pylint: disable=W0212
        #                          Access to protected member
        return self.__class__._set_get(pars, "rev", new_val)
    def path(self, new_val= None):
        """return the path if the type is "path"."""
        (d, type_, pars)= self.unpack()
        if type_!= "path":
            raise TypeError("error, 'path()' can only be called for "
                            "SourceSpec objects of type 'path'")
        if new_val is None:
            return pars
        d[type_]= new_val
        return new_val
    def tar(self, new_val= None):
        """return the tar if the type is "tar"."""
        (d, type_, pars)= self.unpack()
        if type_!= "tar":
            raise TypeError("error, 'tar()' can only be called for "
                            "SourceSpec objects of type 'tar'")
        if new_val is None:
            return pars
        d[type_]= new_val
        return new_val
    def url(self, new_val= None):
        """return the url if the type is a repository."""
        (_, type_, pars)= self.unpack()
        if type_ in known_no_repos:
            raise TypeError("error, 'url()' cannot be called for "
                            "SourceSpec objects of type '%s'" % type_)
        return self._set_get(pars, "url", new_val)
    def spec_dict(self):
        """return a dict with keys "url" and "tag"."""
        if not self.is_repo():
            raise TypeError("error, 'spec_dict()' can only be called for "
                            "SourceSpec objects of type repository")
        d= { "url": self.url()}
        t= self.tag()
        if t:
            d["tag"]= t
        return d
    def unpack(self):
        """return the internal dict, the sourcetype and the parameters.
        """
        d= self.datadict()
        type_= sumolib.utils.single_key(d)
        return (d, type_, d[type_])
    def copy(self, other):
        """simply overwrite self with other."""
        (self_d, self_type, _)= self.unpack()
        (_, other_type, other_pars)= other.unpack()
        del self_d[self_type]
        # reconstruct other_pars if it is an object. For dicts this creates a
        # second independent dict:
        self_d[other_type]= other_pars.__class__(other_pars)
    def change_source(self, other):
        """set source spec by copying information from another object.

        This can also handle wildcards.

        returns True if the spec was changed, False if it wasn't.
        """
        (self_d, self_type, self_pars)   = self.unpack()
        (_, other_type, other_pars)= other.unpack()

        if self_type!=other_type:
            self.copy(other)
            return True

        if isinstance(other_pars, basestring):
            # this is only the case for type "path" or type "tar":
            if other_pars=="*":
                return False
            self_d[self_type]= other_pars
            return True
        if isinstance(other_pars, dict):
            # usually a repository type:
            original= dict(self_pars)
            self_pars.clear()
            changed= False
            for (k,v) in other_pars.items():
                if original.get(k)==v:
                    self_pars[k]= v
                    continue
                if v=="*":
                    v= original.get(k)
                    if v is None:
                        raise ValueError("cannot replace wildcard "
                                         "for key %s" % k)
                    self_pars[k]= v
                    continue
                self_pars[k]= v
                changed= True
            return changed
        else:
            raise AssertionError("unexpected type: %s" % repr(other_pars))
    def change_source_by_tag(self, tag):
        """change the source spec just by providing a tag.

        returns True if the spec was changed, False if it wasn't.
        """
        (_, self_type, self_pars)   = self.unpack()
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
    def __init__(self, repotype, spec, directory, verbose, dry_run):
        """create the object.

        spec must be a dictionary with "url" and "tag" (optional).

        If repotype is None, create an empty object that basically
        does nothing.
        """
        # pylint: disable=R0913
        #                          Too many arguments
        self.repotype= repotype
        if repotype is None:
            return
        self.spec= spec
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        self.repo_obj= None
    def prepare_read(self):
        """do checkout or pull."""
        if self.repotype is None:
            return
        if not os.path.isdir(self.directory):
            # must check out
            checkout(self.repotype, self.spec, self.directory,
                     self.verbose, self.dry_run)
            if not os.path.isdir(self.directory):
                raise AssertionError("checkout of %s %s to %s failed" % \
                                     (self.repotype,
                                      repr(self.spec),
                                      self.directory))
        if not self.repo_obj:
            self.repo_obj= \
                repo_from_dir(self.directory, {}, self.verbose, self.dry_run)
        # pylint: disable=E1103
        #                          Instance of 'Repo' has no 'pull' member
        self.repo_obj.pull()
    def finish_write(self, message):
        """do commit and push."""
        if self.repotype is None:
            return
        if not self.repo_obj:
            raise AssertionError("internal error, repo obj missing")
        # pylint: disable=E1103
        #                          Instance of 'Repo' has no '...' member
        self.repo_obj.commit(message)
        self.repo_obj.push()

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
