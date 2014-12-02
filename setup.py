#!/usr/bin/env python
"""
setup.py file for sumo.

See http://docs.python.org/install
on how to use setup.py
"""
my_version="2.2.2" #VERSION#

from distutils.core import setup

import os
import os.path
import shutil
import glob
import subprocess

# utilities -------------------------

def find_files(path):
    """find files and directories below a given path.

    here is an example of the returned data structure:
    {'doc/_build/html': ['objects.inv', 'searchindex.js', 'index.html'], 
     'doc/_build': [], 
     'doc/_build/html/_sources': ['license.txt', 'index.txt']
     'doc/_build/doctrees': ['SDshell.doctree', 'license.doctree']
    }
    """
    paths= {}
    for dirpath, dirnames, filenames in os.walk(path):
        paths[dirpath]= filenames
    return paths

def pathsplit(path):
    """splits a path into pieces.
    
    Here are some examples:
    >>> pathsplit("A")
    ['A']
    >>> pathsplit("A/B")
    ['A', 'B']
    >>> pathsplit("A/B/C")
    ['A', 'B', 'C']
    >>> pathsplit("A/B.x/C.y")
    ['A', 'B.x', 'C.y']
    """
    l= []
    while True:
        (head,tail)=os.path.split(path)
        l.append(tail)
        if not head:
            break
        path= head
    l.reverse()
    return l

def path_rebase(path, base):
    """rebases a path.

    Here are some examples:
    >>> path_rebase("doc/_build/html/_sources","doc/_build")
    'html/_sources'
    >>> path_rebase("doc/_build/html/_sources","doc/_build/html")
    '_sources'
    >>> path_rebase("doc/_build/html/_sources","doc")
    '_build/html/_sources'
    >>> path_rebase("doc/_build/html/_sources","doc/_bduild")
    'doc/_build/html/_sources'
    """
    path_l= pathsplit(path)
    base_l= pathsplit(base)
    if len(path_l)<len(base_l):
        return path
    for i in xrange(len(base_l)):
        if base_l[i]!=path_l[i]:
            return path
    if len(path_l)==len(base_l):
        return ""
    return os.path.join(*path_l[len(base_l):])

def data_statements(install_path, source_path):
    """create data statements for arbitrary files."""
    filedict= find_files(source_path)
    data_dict= {}
    for (path,files) in filedict.items():
        subdir= path_rebase(path, source_path)
        if subdir != "":
            destpath= os.path.join(install_path, subdir)
        else:
            destpath= install_path
        for f in files:
            l= data_dict.get(destpath)
            if l is None:
                l= []
                data_dict[destpath]= l
            l.append(os.path.join(path, f))
    return data_dict.items()

def copy_files(dest_dir, source_dir, source_files):
    """copy files from source to dest if they are newer.
    """
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    for f in source_files:
        src= os.path.join(source_dir,f)
        dst= os.path.join(dest_dir, f)
        if os.path.exists(dst):
            if os.path.getmtime(dst)>=os.path.getmtime(src):
                continue
        shutil.copyfile(src, dst)

# main      -------------------------

doc_install_dir= os.path.join("doc","sumo-%s" % my_version)
html_install_dir= os.path.join(doc_install_dir, "html")

doc_dir= "doc"

html_build_dir= os.path.join(doc_dir,"_build","html")

## create HTML documentation if it doesn't already exist:
if not os.path.exists(html_build_dir):
    # "make -C doc html":
    subprocess.check_call(["make", "-C", "doc", "html"])


data_files_list= [(doc_install_dir, ["README", "LICENSE"])]

# add all generated html documentation to data_files_list:
data_files_list.extend(data_statements(html_install_dir, html_build_dir))

setup(name='sumo',
      version= my_version,
      description='Python support tools for EPICS software development',
      author='Goetz Pfeiffer',
      author_email='Goetz.Pfeiffer@helmholtz-berlin.de',
      url='http://www-csr.bessy.de/control/sumo',
      packages=['sumolib'],
      #package_dir= {'': 'sumo'},
      #package_data={'sumo': ['data/*']},
      data_files= data_files_list,
      license= "HZB non commercial license, see file LICENSE",
      scripts=['bin/sumo','bin/sumo-scan'],
     )
