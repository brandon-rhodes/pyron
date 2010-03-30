"""The Pyron import hook.

Every time Python starts up, Pyron needs to make sure that every module
under development is ready to be imported should an ``import`` statement
name them.  Therefore, Pyron installs a ``pyron-packages.pth`` file in
the current Python environment's ``site-packages`` directory, and makes
that file call the `install_import_hook()` function defined here.

Because this module is invoked every time Python runs, it deliberately
re-implements small pieces of core Pyron logic - like how to parse a
``pyron.ini`` file - to avoid importing anything but core Python
packages.

"""
from ConfigParser import RawConfigParser, NoOptionError
import imp
import os
import sys

sys.dont_write_bytecode = True

class PyronLoader(object):
    """PEP-302 compliant loader for packages being developed with Pyron."""

    def __init__(self, fullname, package_dir, init_path):
        self.fullname = fullname
        self.package_dir = package_dir
        self.init_path = init_path

    def load_module(self, fullname):
        """Load and return the package."""
        assert fullname == self.fullname  # PyronFinder called right loader
        f = open(self.init_path)
        try:
            m = imp.load_module(fullname, f, self.init_path, ('.py', 'U', 1))
            m.__path__ = [ self.package_dir ]
            return m
        finally:
            f.close()

class PyronFinder(object):
    """PEP-302 compliant finder for packages being developed with Pyron."""

    def __init__(self, loaders):
        self.loaders = {}

    def add(self, fullname, loader):
        """Add a loader for the package named `fullname`."""
        self.loaders[fullname] = loader

    def find_module(self, fullname, path=None):
        """Return the loader for package `fullname` if we have one."""
        return self.loaders.get(fullname, None)

def warn(message):
    sys.stderr.write('Warning: ' + message + '\n')
    sys.stderr.flush()

def install_import_hook(inipaths):
    """Install an import hook for each package whose ``.ini`` file is listed.

    This inspects each ``pyron.ini`` file listed in `inipaths`.  For
    each file, it installs an import finder and loader for the module
    that it describes.

    """
    return
    if not inipaths:
        return

    finder = PyronFinder()

    for inipath in inipaths:
        if not os.path.exists(inipath):
            warn(u'file has gone missing: ' + inipath)
            continue
        config = RawConfigParser()
        config.readfp(open(inipath))
        try:
            fullname = config.get('package', 'name')
        except NoOptionError:
            warn(u'missing "name" in [package] section: ' + inipath)
            continue
        dirpath = os.path.dirname(inipath)
        initpath = os.path.join(dirpath, '__init__.py')
        loader = PyronLoader(fullname, dirpath, initpath)

    sys.meta_path.append(finder)
