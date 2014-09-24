"""Repository support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import re
import sumo.system
import sumo.utils
import sumo.path
import sumo.darcs

rx_darcs_ssh_url= re.compile(r'^([\w_\.]+)@([\w_\.]+):(.*)$')

known_repos=set(("darcs",))
known_sources= set(("path",)).union(known_repos)

# ---------------------------------------------------------
# generic code:

# ---------------------------------------------------------
# scan a directory:

def repo_from_dir(directory, hints, verbose, dry_run):
    """scan a directory and return a repository object.

    Hints must be a dictionary. This gives hints how the directory should be
    scanned. Currently we know these keys in the dictionary:

    "ignore changes": sumo.utils.RegexpMatcher
        All local changes in files that match the RegexpMatcher object are
        ignored. By this we can get the remote repository and tag from a
        directory although there are uncomitted changes. A common application
        is to ignore changes in file "configure/RELEASE".
    "dir patcher": sumo.utils.RegexpPatcher
        This patcher is applied to the directory that is stored in the object.
    "url patcher": sumo.utils.RegexpPatcher
        This patcher is applied to the URL that is stored in the object.
    "force path" : bool
        If this is True, a Path object is always returned, even if a repository
        was found.
    "force local": bool
        If this is True, the returns repository object does not contain a
        remote repoistory url even if there was one.
    """
    if not isinstance(hints, dict):
        raise TypeError("hints parameter '%s' is of wrong type" % \
                        repr(hints))
    if hints.get("force path"):
        return sumo.path.Repo.scan_dir(directory, hints, verbose, dry_run)

    obj= sumo.darcs.Repo.scan_dir(directory, hints, verbose, dry_run)
    if obj is not None:
        return obj
    # insert other repo supports here
    return sumo.path.Repo.scan_dir(directory, hints, verbose, dry_run)

# ---------------------------------------------------------
# check out:

def checkout(repotype, spec, destdir, verbose, dry_run):
    """check out a working copy.
    """
    # pylint: disable=R0913
    #                          Too many arguments
    if repotype == "darcs":
        sumo.darcs.Repo.checkout(spec, destdir, verbose, dry_run)
    elif repotype== "path":
        sumo.path.Repo.checkout(spec, destdir, verbose, dry_run)
    else:
        raise ValueError("unsupported repotype: %s" % repotype)

# ---------------------------------------------------------
# SourceSpec class:

class SourceSpec(sumo.JSON.Container):
    """hold the source specification.
    """
    # pylint: disable=R0904
    #                          Too many public methods
    def __init__(self, dict_= None):
        """create the object."""
        super(SourceSpec, self).__init__(dict_)
    @classmethod
    def from_param(cls, sourcetype, url=None, tag=None, path=None):
        """create by parameters.
        """
        if sourcetype not in known_sources:
            raise ValueError("unknown source type: '%s'" % sourcetype)
        if sourcetype=="path":
            if not path:
                raise ValueError("'path' missing for sourcetype 'path'")
            return cls({"path": path})
        if sourcetype=="darcs":
            if not url:
                raise ValueError("'url' missing for sourcetype 'darcs'")
            d= {"url": url}
            if tag:
                d["tag"]= tag
            return cls({sourcetype: d})
        raise AssertionError("unknown sourcetype: %s" % sourcetype)
    @classmethod
    def from_string_sourcespec(cls, elms):
        """scan a source specification.

        A sourcespec is a list of strings. Currently we support here:
        ["path",PATH] or
        [<repotype>,URL] or [<repotype>,URL,TAG].

        where <repotype> may be one of the strings in
        sumo.repos.known_repos

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
        if elms[0]=="path":
            if len(elms)!=2:
                raise ValueError("invalid source spec: '%s'" % (" ".join(elms)))
            return cls({"path": elms[1]})
        if len(elms)==2:
            return cls({elms[0]:{"url":elms[1]}})
        elif len(elms)==3:
            return cls({elms[0]:{"url":elms[1], "tag":elms[2]}})
        else:
            raise ValueError("invalid source spec: '%s'" % (" ".join(elms)))
    def sourcetype(self):
        """return the type of the source."""
        d= self.datadict()
        return sumo.utils.single_key(d)
    def is_repo(self):
        """return if SourceSpec refers to a repository.
        """
        return self.sourcetype() in known_repos
    def tag(self):
        """return the tag."""
        d= self.datadict()
        type_= sumo.utils.single_key(d)
        return d[type_].get("tag")
    def path(self):
        """return the path if the type is "path"."""
        (_, type_, pars)= self.unpack()
        if type_!= "path":
            raise TypeError("error, 'path()' can only be called for "
                            "SourceSpec objects of type 'path'")
        return pars
    def url(self):
        """return the path if the type is "path"."""
        (_, type_, pars)= self.unpack()
        if type_== "path":
            raise TypeError("error, 'url()' cannot be called for "
                            "SourceSpec objects of type 'path'")
        return pars["url"]
    def unpack(self):
        """return the internal dict, the sourcetype and the parameters.
        """
        d= self.datadict()
        type_= sumo.utils.single_key(d)
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

        if isinstance(other_pars, str):
            # usually type "path":
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
        if self_type=="path":
            raise ValueError("you cannot provide just a new tag for "
                             "a source specification of type 'path'")
        old= self_pars.get("tag")
        if old==tag:
            return False
        self_pars["tag"]= tag
        return True

def _test():
    """perform internal tests."""
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
