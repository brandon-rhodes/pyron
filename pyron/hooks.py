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
import imp
import os
import pkgutil
import sys
from ConfigParser import RawConfigParser, NoOptionError

sys.dont_write_bytecode = True

# Since imp.load_module() will not accept a StringIO() "file" as input,
# we have to provide a real empty file for it to parse!
this_dir = os.path.dirname(os.path.abspath(__file__))
empty_file_path = os.path.join(this_dir, 'empty_file.txt')

class NamespacePackageLoader(object):
    """PEP-302 compliant loader for namespace packages."""

    def load_module(self, fullname):
        """Return a new namespace package that itself contains no code."""
        f = open(empty_file_path)
        try:
            m = imp.load_module(fullname, f, '', ('.py', 'U', 1))
            m.__path__ = pkgutil.extend_path([], fullname)
            return m
        finally:
            f.close()

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

    def __init__(self):
        self.loaders = {}

    def add(self, loader):
        """Add a loader for the package named `fullname`."""
        fullname = loader.fullname
        self.loaders[fullname] = loader
        while '.' in fullname:
            fullname = fullname.rsplit('.')[0]
            self.loaders[fullname] = NamespacePackageLoader()

    def find_module(self, fullname, path=None):
        """Return the loader for package `fullname` if we have one."""
        return self.loaders.get(fullname, None)

def install_import_hook(inipaths):
    """Install an import hook for each package whose ``.ini`` file is listed.

    This inspects each ``pyron.ini`` file listed in `inipaths`.  For
    each file, it installs an import finder and loader for the module
    that it describes.

    """
    if not inipaths:
        return

    finder = PyronFinder()
    error = False

    for inipath in inipaths:
        if not os.path.exists(inipath):
            error = True
            continue
        config = RawConfigParser()
        config.readfp(open(inipath))
        try:
            fullname = config.get('package', 'name')
        except NoOptionError:
            error = True
            continue
        dirpath = os.path.dirname(inipath)
        initpath = os.path.join(dirpath, '__init__.py')
        loader = PyronLoader(fullname, dirpath, initpath)
        finder.add(loader)

        # Lie for now.
        version = '1.1'

        # Experiment with adding distribution data to pkg_requires
        import pkg_resources
        #print pkg_resources.working_set.by_key
        #print type(pkg_resources.working_set.by_key['pip'])
        print "HERE", fullname
        dist = pkg_resources.Distribution(
            project_name=fullname,
            version=version,
            )
        dist._ep_map = {
            'console_scripts': {
                'cursive': pkg_resources.EntryPoint(
                    name='cursive',
                    module_name='cursive.tools.cursive',
                    attrs=('console_script_cursive',),
                    dist=dist,
                    ),
                },
            }
        pkg_resources.working_set.by_key[fullname] = dist

    if error:
        sys.stderr.write('Warning: Pyron environment damaged;'
                         ' run "pyron status" for details\n\n')
        sys.stderr.flush()

    sys.meta_path.append(finder)
    #import cursive.tools
    print "DDDDDOOOOOOOONNNNNNNNNE"
