"""Routines for managing the Pyron ``.pth`` file.

When the ``pyron`` command is used to activate a development package,
the package is added to a list of active packages contained in the
``pyron-packages.pth`` file in Python's ``site-packages`` directory.
This module contains both the routines with which Pyron manages its
``.pth``, and also the ``hook()`` function which the file itself calls
during Python startup to get the Pyron-governed packages ready to be
imported.

import pyron.pth; pyron.pth.import()
"""
import os
import sys

FILENAME = 'pyron-packages.pth'
TEMPLATE = """\
# This .pth file is generated and maintained by Pyron.  You can run
# "pyron list" to review which Python projects are listed here.  Use the
# "pyron add" and "pyron remove" commands to modfiy this list.
import pyron.pth; pyron.pth.activate(%r)
"""

def _pth_path():
    """Compute where the Pyron ``.pth`` file should live, if it exists."""
    for p in sys.path:
        if os.path.basename(p) == 'site-packages':
            return os.path.join(p, FILENAME)

def pth_load():
    """Return the ``.ini`` files in the current Pyron ``.pth`` file."""
    p = _pth_path()
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

def _pth_save(paths):
    """Save a list of ``.ini`` file paths to the Pyron ``.pth`` file.

    This overwrites the current version of the file, destroying any
    information there and rewriting it from scratch.

    """
    p = _pth_path()
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
    _pth_save(ini_paths)

def remove(p):
    pass

def activate(ini_paths):
    """"""
    pass
