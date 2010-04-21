"""The Pyron import hook.

Every time a Pyron-powered Python installation starts up, the
``pyron-packages.pth`` file that Pyron has placed in ``site-packages``
invokes the `install_import_hook()` method given below.  This method has
three tasks:

1. Inspect and build a list of all of the currently active Pyron
   development packages.

2. Install a Pyron-specific import "finder" on `sys.meta_path` that can
   import the development packages if they are asked for.

3. Create a Distribution object for each development package, and
   install it in the `pkg_resources` central registry so that its entry
   points are available if queried.

"""
import imp
import os
import pkgutil
import sys

# Ugh, the setuptools.
import pkg_resources

import pyron.project

sys.dont_write_bytecode = True

# Since imp.load_module() will not accept a StringIO() "file" as input,
# we have to provide a real empty file for it to parse!

this_dir = os.path.dirname(os.path.abspath(__file__))
empty_init_path = os.path.join(this_dir, 'empty_init.py.txt')

#
# The package finder and loaders and power the importation of
# development packages.
#

class NamespacePackageLoader(object):
    """PEP-302 compliant loader for namespace packages."""

    def load_module(self, fullname):
        """Return a new namespace package."""
        f = open(empty_init_path)
        try:
            m = imp.load_module(fullname, f, '', ('.py', 'U', 1))
            m.__path__ = pkgutil.extend_path([], fullname)
            return m
        finally:
            f.close()

class PyronPackageLoader(object):
    """PEP-302 compliant loader for packages being developed with Pyron."""

    def __init__(self, fullname, package_dir):
        self.fullname = fullname
        self.package_dir = package_dir

    def load_module(self, fullname):
        """Load and return the package."""
        assert fullname == self.fullname  # PyronFinder called right loader
        init_path = os.path.join(self.package_dir, '__init__.py')
        f = open(init_path)
        try:
            m = imp.load_module(fullname, f, init_path, ('.py', 'U', 1))
            m.__path__ = [ self.package_dir ]
            return m
        finally:
            f.close()

class Finder(object):
    """PEP-302 compliant finder for packages being developed with Pyron."""

    def __init__(self):
        self.loaders = {}

    def add(self, loader):
        """Add the given loader to this finder.

        If loader's package name contains a dot, then the package's
        parent packages are also generated as empty namespace packages.

        """
        fullname = loader.fullname
        self.loaders[fullname] = loader
        while '.' in fullname:
            fullname = fullname.rsplit('.')[0]
            self.loaders[fullname] = NamespacePackageLoader()

    def find_module(self, fullname, path=None):
        """Return the loader for package `fullname`, if we have one."""
        return self.loaders.get(fullname, None)

#
# The function called directly from the ``pyron-packages.pth`` file.
#

def install_import_hook(project_dirs):
    """Given a list of ``pyron.ini`` paths, install package import hooks. 

    This inspects each Pyron project having an ``.ini`` file listed in
    `inipaths`.  For each project, it installs an import finder and
    loader for the package under development.

    """
    if not project_dirs:
        return

    finder = Finder()
    error = False

    for project_dir in project_dirs:

        dist = pyron.project.Project(project_dir).prdist

        loader = PyronPackageLoader(dist.project_name, project_dir)
        finder.add(loader)

        # Add the development distribution to the pkg_resources working
        # set, but refuse to let its path get added to sys.path.  This
        # might be dangerous if pkg_resources later winds up expecting
        # "sys.path" and its own "entries" to match, in which case the
        # "sys.path" entry could perhaps be disabled rather than simply
        # removed.

        pkg_resources.working_set.add(dist)
        sys.path.remove(dist.location)

    if error:
        sys.stderr.write('Warning: Pyron environment damaged;'
                         ' run "pyron status" for details\n\n')
        sys.stderr.flush()

    sys.meta_path.append(finder)
