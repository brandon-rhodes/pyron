import imp
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
        """The `loaders` should map package names to PyronLoader objects."""
        self.loaders = loaders

    def find_module(self, fullname, path=None):
        """If we have a loader for this package, return it, else None."""
        return self.loaders.get(fullname, None)
