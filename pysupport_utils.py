"""Utilities for the pysupport scripts.
"""
import sys

# pylint: disable=C0322

if sys.version_info[0]>2 or (sys.version_info[0]==2 and sys.version_info[1]>5):
    import json
    _JSON_TYPE= 1
else:
    import simplejson as json
    _JSON_TYPE= 0

def json_dump(var):
    """Dump a variable in JSON format.

    Here is an example:
    >>> var= {"key":[1,2,3], "key2":"val", "key3":{"A":1,"B":2}}
    >>> json_dump(var)
    {
        "key": [
            1,
            2,
            3
        ],
        "key2": "val",
        "key3": {
            "A": 1,
            "B": 2
        }
    }
    """
    if _JSON_TYPE==0:
        print json.dumps(var, sort_keys= True, indent= 4*" ")
    else:
        print json.dumps(var, sort_keys= True, indent= 4)

def json_loadfile(filename):
    """load a JSON file.
    """
    fh= open(filename)
    results= json.load(fh)
    fh.close()
    return results

def show_progress(cnt, cnt_max, message= None):
    """show progress on stderr.
    """
    if message:
        sys.stderr.write("'.' for every %s %s\n" % (cnt_max, message))
    cnt-= 1
    if cnt<0:
        sys.stderr.write(".")
        sys.stderr.flush()
        cnt= cnt_max
    return cnt


