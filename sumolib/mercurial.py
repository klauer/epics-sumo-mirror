"""mercurial support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import os.path
import sumolib.system
import re

class Repo(object):
    """represent a mercurial repository."""
    # pylint: disable=R0902
    #                          Too many instance attributes
    rx_tag=re.compile(r'^(.*)\s+([0-9]+):([a-z0-9]+)$')
    def _default_repo(self):
        """return the default repo."""
        try:
            (reply,_)= sumolib.system.system("hg paths default -R %s" % \
                                    self.directory,
                                    True, False,
                                    self.verbose, self.dry_run)
        except IOError, _:
            # probably no repo found
            return
        st= reply.splitlines()[0].strip()
        if st.startswith("not found"):
            return
        return st
    def _find_remote(self, patcher):
        """find and contact the remote repository."""
        default_repo= self._default_repo()
        if default_repo is None:
            return
        if patcher is not None:
            default_repo= patcher.apply(default_repo)
        cmd= "hg -R %s incoming %s" % \
                 (self.directory, default_repo)
        (_,_,rc)= sumolib.system.system_rc(cmd,
                             True, True,
                             self.verbose, self.dry_run)
        if rc not in (0,1):
            # contacting the remote repo failed
            return
        return default_repo
    def _local_changes(self, matcher):
        """returns True if there are uncomitted changes.

        Does basically "hg status". All lines that match the matcher
        object are ignored. The matcher parameter may be <None>.
        """
        cmd= "hg status -a -m -r -d -R %s" % self.directory
        (reply,_,rc)= sumolib.system.system_rc(cmd,
                             True, False, self.verbose, self.dry_run)
        # Note: a return code 1 is normal with mercurial
        if rc not in (0,1):
            raise IOError(rc, "cmd \"%s\" failed" % cmd)
        changes= False
        for line in reply.splitlines():
            line= line.strip()
            if matcher is not None:
                # ignore if line matches:
                if matcher.search(line):
                    continue
            # any line remaining means that there were changes:
            changes= True
            break
        return changes
    def _local_patches(self):
        """returns True when there are unpushed patches.

        """
        if self.remote_url is None:
            raise AssertionError("cannot compute local patches without "
                                 "a reachable remote repository.")
        cmd= "hg -R %s outgoing" % self.directory
        (_,_,rc)= sumolib.system.system_rc(cmd,
                             True, False, self.verbose, self.dry_run)
        if rc not in (0,1):
            raise IOError(rc, "cmd \"%s\" failed" % cmd)
        return rc==0
    def _current_revision(self):
        """returns the revision of the working copy.
        """
        (reply,_)= sumolib.system.system("hg identify -i -R %s" % \
                                self.directory,
                                True, False,
                                self.verbose, self.dry_run)
        # for uncomitted changes, the revision ends with a "+":
        return reply.splitlines()[0].strip().replace("+","")
    def _tag_on_top(self):
        """returns True when a tag identifies the working copy.

        These automatically generated tags are ignored:
          tip, qtip, qbase, qparent

        Returns the found tag or None if no tag on top was found.
        """
        ignore= set(("tip","qtip","qbase","qparent"))
        curr_rev= self.current_revision
        cmd= "hg tags -R %s" % self.directory
        (reply,_)= sumolib.system.system(cmd,
                             True, False,
                             self.verbose, self.dry_run)
        tags= []
        for line in reply.splitlines():
            line= line.strip()
            m= self.__class__.rx_tag.search(line)
            if m is None:
                raise AssertionError("cannot parse: '%s' % line")
            tag= m.group(1).strip()
            if tag in ignore:
                continue
            if m.group(3)==curr_rev:
                tags.append(m.group(1).strip())
        if not tags:
            # no tags found:
            return
        # return the first tag of the sorted list:
        tags.sort()
        return tags[0]
    def _hint(self, name):
        """return the value of hint "name"."""
        return self.hints.get(name)
    def __init__(self, directory, hints, verbose, dry_run):
        """initialize.

        Hints must be a dictionary. This gives hints how the directory should
        be scanned. Currently we know these keys in the dictionary:

        "ignore changes": sumolib.utils.RegexpMatcher
            All local changes in files that match the RegexpMatcher object are
            ignored. By this we can get the remote repository and tag from a
            directory although there are uncomitted changes. A common
            application is to ignore changes in file "configure/RELEASE".
        "dir patcher": sumolib.utils.RegexpPatcher
            This patcher is applied to the directory that is stored in the
            object.
        "url patcher": sumolib.utils.RegexpPatcher
            This patcher is applied to the URL that is stored in the object.
        "force local": bool
            If this is True, the returns repository object does not contain a
            remote repoistory url even if there was one.
        """
        self.hints= dict(hints) # shallow copy
        patcher= self._hint("dir patcher")
        if patcher is not None:
            directory= patcher.apply(directory)
        self.directory= directory
        self.verbose= verbose
        self.dry_run= dry_run
        self.local_changes= None
        self.remote_url= None
        self.local_patches= None
        self.tag_on_top= None
        self.current_revision= None
        if self.directory is None:
            return
        self.current_revision= self._current_revision()
        self.local_changes= \
                self._local_changes(self._hint("ignore changes"))
        self.remote_url= self._find_remote(self._hint("url patcher"))
        if self.remote_url is not None:
            self.local_patches= self._local_patches()
        if self._hint("force local"):
            self.remote_url= None
        self.tag_on_top= self._tag_on_top() # uses self._current_revision
    def __str__(self):
        """return a human readable representation."""
        lines= [ "mercurial repo",
                 "dir: %s" % repr(self.directory),
                 "current revision: %s" % repr(self.current_revision),
                 "local_changes: %s" % repr(self.local_changes),
                 "remote url: %s" % repr(self.remote_url),
                 "local patches: %s" % repr(self.local_patches),
                 "tag on top: %s" % repr(self.tag_on_top) ]
        return "\n".join(lines)
    def name(self):
        """return the repo type name."""
        # pylint: disable=R0201
        #                          Method could be a function
        return "hg"
    def get_tag_on_top(self):
        """return the "tag on top" property."""
        return self.tag_on_top
    def get_revision(self):
        """return the current revision."""
        return self.current_revision
    @classmethod
    def scan_dir(cls, directory, hints, verbose, dry_run):
        """return a Repo object if a mercurial repo was found.

        This function returns <None> if no working repo was found.

        For parameter "hints" see comment at __init__.
        """
        # pylint: disable=R0201
        #                          Method could be a function
        if not os.path.exists(os.path.join(directory,".hg")):
            return
        obj= cls(directory, hints, verbose, dry_run)
        # if there are unrecorded changes we cannot use this as a repository,
        # we have to copy the whole directory instead:
        if obj.local_changes:
            return
        return obj
    def source_spec(self):
        """return a complete source specification (for SourceSpec class).
        """
        if self.directory is None:
            raise AssertionError("cannot create source_spec from "
                                 "empty object")
        if self.local_changes:
            raise AssertionError("cannot create spec from repo '%s' with "
                                 "unrecorded changes" % self.directory)
        pars= {}
        d= {"hg": pars}
        if self.tag_on_top is not None:
            pars["tag"]= self.tag_on_top
        else:
            pars["rev"]= self.current_revision

        if self.remote_url is None:
            pars["url"]= self.directory
        elif self.local_patches:
            pars["url"]= self.directory
        else:
            pars["url"]= self.remote_url
        return d
    @staticmethod
    def checkout(spec, destdir, verbose, dry_run):
        """spec must be a dictionary with "url" and "tag" (optional).
        """
        cmd_l= ["hg", "clone"]
        url= spec.get("url")
        if url is None:
            raise ValueError("spec '%s' has no url" % repr(spec))
        tag= spec.get("tag")
        rev= spec.get("rev")
        if tag and rev:
            raise ValueError("you cannot specify both, tag '%s' and "
                             "revision '%s'" % (tag,rev))
        if tag is not None:
            cmd_l.extend(["-u '%s'" % tag])
        elif rev is not None:
            cmd_l.extend(["-u '%s'" % rev])
        cmd_l.append(url)
        cmd_l.append(destdir)
        cmd= " ".join(cmd_l)
        sumolib.system.system(cmd, False, False, verbose, dry_run)
