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

def bin_path():
    """Compute where console scripts should be installed."""
    return os.path.join(sys.prefix, 'bin')

#
# Complex, unhappy routines to fool the setuptools into creating console
# scripts for us (so that we do not have to figure out how to create
# them under Windows and so forth).
#

class FakeDistribution(object):
    """Class enough like a Distribution to power script installation.

    By using this simple class to power the ``easy_install`` method that
    creates wrapper scripts, we provide it with enough information
    without having to rely on the ``setuptools`` ``Distribution`` object
    with all of its complexity (which, when ``setuptools`` is imported,
    is also monkey-patched in place of ``distutils.dist.Distrubtion``).

    """
    def __init__(self, dist):
        self.dist = dist

    def as_requirement(self):
        return '%s=%s' % (self.dist.name, self.dist.version)

    def get_entry_map(self, group):
        return self.dist.entry_points.get(group, None) or {}

def add_scripts(dist):
    """Create console scripts for the given distribution."""

    # Only import setuptools when finally necessary
    import setuptools.command.easy_install

    class Neutered_easy_install(setuptools.command.easy_install.easy_install):
        def __init__(self):
            """Fake a bare-minimum setup of a Command object."""
            self.dry_run = False
            self.exclude_scripts = False
            self.script_dir = bin_path()

        def add_output(self, path):
            """Do nothing."""

    fakedist = FakeDistribution(dist)
    easy_install = Neutered_easy_install()
    easy_install.install_wrapper_scripts(fakedist)

#
# Simple, happy routines for writing and updating our own ".pth" file.
#

FILENAME = 'pyron-packages.pth'
TEMPLATE = """\
# This .pth file is generated and maintained by Pyron.  Run "pyron help"
# to learn about the sub-commands with which you can view, modify, and
# manage this list of development packages.
import pyron.hooks; pyron.hooks.install_import_hook(%r)
"""

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