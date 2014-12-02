"""darcs support
"""

# pylint: disable=C0103
#                          Invalid name for type variable

import re
import os.path
import sumolib.system

__version__="2.2.2" #VERSION#

assert __version__==sumolib.system.__version__

# -----------------------------------------------
# Repo class
# -----------------------------------------------

class Repo(object):
    """represent a darcs repository."""
    # pylint: disable=R0902
    #                          Too many instance attributes
    rx_darcs_repo= re.compile(r'^\s*Default Remote:\s*(.*)')
    def _default_repo(self):
        """return the default repo."""
        try:
            (reply,_)= sumolib.system.system(
                                    "darcs show repo --repodir %s" % \
                                        self.directory,
                                    True, False,
                                    self.verbose, self.dry_run)
        except IOError, _:
            # probably no darcs repo found
            return
        for line in reply.splitlines():
            m= self.__class__.rx_darcs_repo.match(line)
            if m:
                return m.group(1).strip()
        return
    def _find_remote(self, patcher):
        """find and contact the remote repository."""
        default_repo= self._default_repo()
        if default_repo is None:
            return
        if patcher is not None:
            default_repo= patcher.apply(default_repo)
        cmd= "darcs pull '%s' --repodir %s --dry-run" % \
                 (default_repo, self.directory)
        try:
            # catch_stdout= True : do not show stdout,
            # catch_stderr= True : do not show stderr:
            (_,_)= sumolib.system.system(cmd,
                                 True, True,
                                 self.verbose, self.dry_run)
        except IOError, _:
            # probably no darcs repo found
            return
        return default_repo
    def _local_changes(self, matcher):
        """returns True if there are unrecorded changes.

        Does basically "darcs whatsnew". All lines that match the matcher
        object are ignored. The matcher parameter may be <None>.
        """
        cmd= "darcs whatsnew -s --repodir %s" % self.directory
        (reply,_,rc)= sumolib.system.system_rc(cmd,
                             True, False, self.verbose, self.dry_run)
        # Note: a return code 1 is normal with darcs
        if rc not in (0,1):
            raise IOError(rc, "cmd \"%s\" failed" % cmd)
        changes= False
        for line in reply.splitlines():
            line= line.strip()
            if matcher is not None:
                # ignore if line matches:
                if matcher.search(line):
                    continue
            if line.startswith("No changes"):
                continue
            changes= True
            break
        return changes
    def _local_patches(self):
        """returns True when there are unpushed patches.

        """
        if self.remote_url is None:
            raise AssertionError("cannot compute local patches without "
                                 "a reachable remote repository.")
        cmd= "darcs push --repodir %s --dry-run" % self.directory
        (reply,_)= sumolib.system.system(cmd,
                             True, False,
                             self.verbose, self.dry_run)
        last_line= reply.splitlines()[-1].strip()
        if last_line.startswith("No recorded local changes"):
            return False
        return True
    def _tag_on_top(self):
        """returns True when a darcs tag is the first in the patch list.

        For a "clean" darcs repository the first patch shown with "darcs
        changes" should be a tag.

        Returns the found tag or None if no tag on top was found.
        """
        cmd= "darcs changes --last 1 --repodir %s" % self.directory
        (reply,_)= sumolib.system.system(cmd,
                             True, False,
                             self.verbose, self.dry_run)
        last_line= reply.splitlines()[-1].strip()
        if last_line.startswith("tagged "):
            return last_line.replace("tagged ","")
        return None
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
        if not isinstance(hints, dict):
            raise TypeError("hints parameter '%s' has wrong type" % \
                            repr(hints))
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
        if self.directory is None:
            return
        self.local_changes= \
                self._local_changes(self._hint("ignore changes"))
        self.remote_url= self._find_remote(self._hint("url patcher"))
        if self.remote_url is not None:
            self.local_patches= self._local_patches()
        if self._hint("force local"):
            self.remote_url= None
        self.tag_on_top= self._tag_on_top()
    def __str__(self):
        """return a human readable representation."""
        lines= [ "darcs repo",
                 "dir: %s" % repr(self.directory),
                 "local_changes: %s" % repr(self.local_changes),
                 "remote url: %s" % repr(self.remote_url),
                 "local patches: %s" % repr(self.local_patches),
                 "tag on top: %s" % repr(self.tag_on_top) ]
        return "\n".join(lines)
    def name(self):
        """return the repo type name."""
        # pylint: disable=R0201
        #                          Method could be a function
        return "darcs"
    def get_tag_on_top(self):
        """return the "tag on top" property."""
        return self.tag_on_top
    @classmethod
    def scan_dir(cls, directory, hints, verbose, dry_run):
        """return a Repo object if a darcs repo was found.

        This function returns <None> if no working repo was found.

        If bool(hints["write check"]) is True, return <None> if the repository
        directory is not writable.

        For parameter "hints" see comment at __init__.
        """
        # pylint: disable=R0201
        #                          Method could be a function
        repodir= os.path.join(directory,"_darcs")
        if not os.path.exists(repodir):
            return
        if hints.get("write check"):
            if not os.access(repodir, os.W_OK):
                return
        obj= cls(directory, hints, verbose, dry_run)
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
        d= {"darcs": pars}
        if self.tag_on_top is not None:
            pars["tag"]= self.tag_on_top

        if self.remote_url is None:
            pars["url"]= self.directory
        elif self.local_patches:
            pars["url"]= self.directory
        elif self.tag_on_top is None:
            pars["url"]= self.directory
        else:
            pars["url"]= self.remote_url
        return d
    @staticmethod
    def checkout(spec, destdir, verbose, dry_run):
        """spec must be a dictionary with "url" and "tag" (optional).
        """
        cmd_l= ["darcs", "get"]
        url= spec.get("url")
        if url is None:
            raise ValueError("spec '%s' has no url" % repr(spec))
        tag= spec.get("tag")
        if tag is not None:
            cmd_l.extend(["-t", r"'^%s\s*$'" % tag])
        cmd_l.append("-q")
        cmd_l.append(url)
        cmd_l.append(destdir)
        cmd= " ".join(cmd_l)
        sumolib.system.system(cmd, False, False, verbose, dry_run)
    def commit(self, logmessage):
        """commit changes."""
        if not logmessage:
            m_param=""
        else:
            m_param="-m '%s'" % logmessage
        cmd="darcs record --repodir %s -a %s" % (self.directory, m_param)
        (_,_)= sumolib.system.system(cmd,
                                     True, False,
                                     self.verbose, self.dry_run)
        self.local_changes= False
    def push(self):
        """push all changes changes."""
        cmd="darcs push --repodir %s -a %s" % (self.directory,
                                               self.remote_url)
        (_,_)= sumolib.system.system(cmd,
                                     True, False,
                                     self.verbose, self.dry_run)
    def pull_merge(self):
        """pull changes and try to merge."""
        cmd="darcs pull --repodir %s -q -a %s" % (self.directory,
                                                  self.remote_url)
        (stdout,_)= sumolib.system.system(cmd,
                                          True, False,
                                          self.verbose, self.dry_run)
        print stdout
        for l in stdout.splitlines():
            if l.lower().startswith("we have conflicts"):
                msg="error, 'darcs pull' failed"
                raise IOError(msg)

