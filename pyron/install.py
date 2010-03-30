"""Routines for managing the current Python installation.

Pyron alters the Python installation in which it has been installed.
This should generally be a virtualenv, though some developers might try
using Pyron with their system Python, or with an instance of Python that
they have built with a different "--prefix".  Pyron makes two changes to
its home installtion:

* It creates a "pyron-packages.pth" file in "site-packages" that tells
  Python how to import the development packages that have been activated
  with "pyron add".

* It creates and deletes console scripts in the "bin" directory as
  development packages are added and deleted.

"""
import os
import sys

FILENAME = 'pyron-packages.pth'
TEMPLATE = """\
# This .pth file is generated and maintained by Pyron.  Run "pyron help"
# to learn about the sub-commands with which you can view, modify, and
# manage this list of development packages.
import pyron.hooks; pyron.hooks.install_import_hook(%r)
"""

def bin_path():
    """Compute where console scripts should be installed."""
    return os.path.join(sys.prefix, 'bin')

def pth_path():
    """Compute where the Pyron ``.pth`` file should live, if it exists."""
    for p in sys.path:
        if os.path.basename(p) == 'site-packages':
            return os.path.join(p, FILENAME)

def pth_load():
    """Return the ``.ini`` files in the current Pyron ``.pth`` file."""
    p = pth_path()
    if p is not None and os.path.isfile(p):
        lines = open(p).readlines()
        if lines:
            lastline = lines[-1]
            expression = lastline.rsplit('(')[-1].split(')')[0]
            if expression and expression != lastline:
                ini_list = eval(expression)
                return ini_list
    # If the attempt to read the .pth file fails, return an empty list.
    return []

def pth_save(paths):
    """Save a list of ``.ini`` file paths to the Pyron ``.pth`` file.

    This overwrites the current version of the file, destroying any
    information there and rewriting it from scratch.

    """
    p = pth_path()
    f = open(p, 'w')
    f.write(TEMPLATE % (paths,))
    f.close()

def _pth_packages():
    """Return a Package for each ``.ini`` in the Pyron ``.pth`` file."""
    ini_list = _pth_load()
    return ini_list

def list():
    """Display a list of currently active packages."""
    packages = _pth_packages()
    print packages

def add(paths):
    """Add a list of paths to the paths already in our ``.pth`` file."""
    ini_paths = pth_load()
    ini_paths.extend(paths)
    pth_save(ini_paths)

def remove(p):
    pass
