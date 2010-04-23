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
import setuptools.command.easy_install

from pyron.exceptions import PyronError

def bin_path():
    """Compute where console scripts should be installed."""
    return os.path.join(sys.prefix, 'bin')

#
# Complex, unhappy routine to fool the setuptools into creating console
# scripts for us (so that we do not have to figure out how to create
# them under Windows and so forth).
#

class Neutered_easy_install(setuptools.command.easy_install.easy_install):
    def __init__(self):
        """Fake a bare-minimum setup of a Command object."""
        self.dry_run = False
        self.exclude_scripts = False
        self.script_dir = bin_path()

    def add_output(self, path):
        """Do nothing (callback used by install_wrapper_scripts)."""

def add_scripts(dist):
    """Create console scripts for the given distribution."""
    easy_install = Neutered_easy_install()
    easy_install.install_wrapper_scripts(dist)

def remove_scripts(dist):
    """Remove the console scripts of a distribution."""
    easy_install = Neutered_easy_install()
    for args in setuptools.command.easy_install.get_script_args(dist):
        script_name = args[0]
        target = os.path.join(easy_install.script_dir, script_name)
        os.unlink(target)

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
    """Return the paths in the current Pyron ``.pth`` file."""
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
    """Save a list paths to the Pyron ``.pth`` file.

    This overwrites the current version of the file, destroying any
    information there and rewriting it from scratch.

    """
    p = pth_path()
    f = open(p, 'w')
    uniq_paths = []  # during development, make multiple "add"s idempotent
    for p in paths:
        if p not in uniq_paths:
            uniq_paths.append(p)
    f.write(TEMPLATE % (uniq_paths,))
    f.close()

#
# Routines that do everything to add or remove a distribution.
#

def add(dist):
    """Add a Pyron project to our installation."""
    project_paths = pth_load()
    if dist.location in project_paths:
        raise PyronError('already installed: ' + dist.location)
    project_paths.append(dist.location)
    add_scripts(dist)
    pth_save(project_paths)

def remove(dist):
    """Remove a Pyron project from our installation."""
    project_paths = pth_load()
    project_paths.remove(dist.location)
    remove_scripts(dist)
    pth_save(project_paths)
