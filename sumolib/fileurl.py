"""urlsupport"""

# pylint: disable=C0103
#                          Invalid name for type variable

import re
import shutil
import urllib
import sumolib.system

__version__="2.3.1" #VERSION#

assert __version__==sumolib.system.__version__

rx_url= re.compile(r'([A-Za-z][A-Za-z0-9\.+-]*):')

urllib_schemes= set(("http","ftp","file"))

def get(url, dest, verbose, dry_run):
    """Get by url."""
    m= rx_url.match(url)
    if m is None:
        # try to copy:
        shutil.copyfile(url, dest)
        return
    scheme_name= m.group(1)
    if scheme_name=="ssh":
        if not url.startswith("ssh://"):
            raise ValueError("error, ssh url '%s' not supported" % url)
        st= url.replace("ssh://","",1)
        cmd= "scp \"%s\" \"%s\"" % (st, dest)
        sumolib.system.system(cmd, False, False, verbose, dry_run)
        return
    if scheme_name in urllib_schemes:
        urllib.urlretrieve(url, dest)
        return
    raise ValueError("error, url '%s' not supported" % url)
