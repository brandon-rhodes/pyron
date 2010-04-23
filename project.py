"""Routines for building a setuptools ``Distribution`` object."""

import email.utils
import os
import pkg_resources
import setuptools.dist
from fnmatch import fnmatch

import pyron.config
import pyron.readme
from pyron.exceptions import PyronError
from pyron.introspect import parse_project_init

EXCLUDE_PATTERNS = ('.*', '*.pyc', '*.pyo', 'pyron.ini', 'entry_points.ini')

class Project(object):
    """Information about a particular Pyron-powered project.

    When a `Project` object is created, a quick inspection of its main
    directory is performed to determine the project's metadata.  Further
    information is pulled if the caller triggers the creation of either
    of two important sub-objects, which are built lazily on demand:

    - `project.prdist` is a `pkg_resources.Distribution` instance which
      parses the ``entry_points.ini`` file for entry point information,
      if that file is present.

    - `project.sddist` is a `setuptools.dist.Distribution` instance
      which needs the project documentation defined in ``README.txt``.

    """
    def __init__(self, project_dir):
        self.dir = project_dir
        self.config = pyron.config.read_pyron_ini(self.file('pyron.ini'))
        self.consts = parse_project_init(self.file('__init__.py'))

        self.namespace_packages = []
        self.name = s = self.config.get('package', 'name')
        while '.' in s:
            s = s.rsplit('.', 1)[0]
            self.namespace_packages[0:0] = [ s ]  # prepend
        self.top_level = s

        self.version = self.consts['__version__']
        if self.config.has_option('package', 'requires'):
            self.requirements = self.config.get('package', 'requires').split()
        else:
            self.requirements = []

        if self.config.has_option('package', 'classifiers'):
            lines = self.config.get('package', 'classifiers').split('\n')
            lines = [ line.strip() for line in lines ]
            self.classifiers = [ line for line in lines if line ]
        else:
            self.classifiers = []

    # Author and author email are parsed from the same field.

    def parse_author(self):
        field = self.config.get('package', 'author')
        self.author, self.author_email = email.utils.parseaddr(field)
        if not self.author:
            raise PyronError(
                'the "author" defined in your "pyron.ini" must include both'
                ' a name and an email address, like "Ed <ed@example.com>"')

    def parse_url(self):
        self.url = self.config.get('package', 'url')

    # Routines to find and read project files.

    def file(self, name):
        """Return the path to the file `name` in the project directory."""
        return os.path.join(self.dir, name)

    def read_entry_points(self):
        """Return the text of the ``entry_points.ini`` file, or None."""
        path = self.file('entry_points.ini')
        if os.path.exists(path):
            f = open(path)
            try:
                text = f.read()
            finally:
                f.close()
            return text
        return None

    def read_readme(self):
        readme_path = pyron.readme.find_readme(self.dir)
        return pyron.readme.inspect_readme(readme_path)

    # Routines to marshal our data into other data structures.

    @property
    def prdist(self):
        """Return a `pkg_resources.Distribution` for this project."""
        prdist = pkg_resources.Distribution(
            location=self.dir,
            project_name=self.name,
            version=self.version,
            )
        text = self.read_entry_points()
        if text:
            prdist._ep_map = pkg_resources.EntryPoint.parse_map(text, prdist)

        self.__dict__['prdist'] = prdist # cache value
        return prdist

    @property
    def sddist(self):
        """Return a `setuptools.dist.Distribution` for this project."""
        sddist = setuptools.dist.Distribution()
        sddist.metadata.name = self.name
        sddist.metadata.version = self.version

        p, sddist.metadata.description, sddist.metadata.long_description \
            = self.read_readme()

        self.parse_author()
        sddist.metadata.author = self.author
        sddist.metadata.author_email = self.author_email

        self.parse_url()
        sddist.metadata.url = self.url

        sddist.metadata.classifiers = self.classifiers

        self.__dict__['sddist'] = sddist # cache value
        return sddist

    def should_include(self, filename):
        """Return whether we should ignore `filename`."""
        for pattern in EXCLUDE_PATTERNS:
            if fnmatch(filename, pattern):
                return False
        return True

    def find_files(self):
        """Yield the (abspath, relpath) to each file in this project."""
        for dirpath, dirnames, filenames in os.walk(self.dir):

            # Prune directories that we should ignore.
            for n in range(len(dirnames) - 1, -1, -1):
                if not self.should_include(dirnames[n]):
                    del dirnames[n]

            # Include appropriate files.
            for filename in filenames:
                if self.should_include(filename):
                    filepath = os.path.join(dirpath, filename)
                    yield filepath, os.path.relpath(filepath, self.dir)
