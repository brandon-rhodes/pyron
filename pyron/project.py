"""Routines for building a setuptools ``Distribution`` object."""

import email.utils
import os
import pkg_resources
import setuptools.dist

import pyron.config
import pyron.readme
from pyron.introspect import parse_project_init

class Project(object):
    """Information about a particular Pyron-powered project.

    When a `Project` object is created, a quick inspection of its main
    directory is performed to determine the project's metadata.  Further
    information is pulled if the caller triggers the creation of either
    of two important sub-objects, which are built lazily on demand:

    - `project.prdist` is a `pkg_resources.Distribution` instance which
      parses the ``entry_points.ini`` file for entry point information,
      if that file is present.

    - `project.dddist` is a `distutils.dist.Distribution` instance
      which needs the project documentation defined in ``README.txt``.

    """
    def __init__(self, project_dir):
        self.dir = project_dir
        self.config = pyron.config.read_pyron_ini(self.file('pyron.ini'))
        self.consts = parse_project_init(self.file('__init__.py'))
        self.name = self.config.get('package', 'name')
        self.version = self.consts['__version__']
        if self.config.has_option('package', 'requires'):
            self.requires = self.config.get('package', 'requires').split()
        else:
            self.requires = []

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
        """Return a `distutils.dist.Distribution` for this project."""
        sddist = setuptools.dist.Distribution()
        sddist.metadata.name = self.name
        sddist.metadata.version = self.version

        author = self.config.get('package', 'author')
        sddist.metadata.author, sddist.metadata.author_email \
            = email.utils.parseaddr(author)
        if not sddist.metadata.author:
            die('the "author" defined in your "pyron.ini" must include both'
                ' a name and an email address, like "Ed <ed@example.com>"')

        sddist.metadata.url = self.config.get('package', 'url')

        readme_path = pyron.readme.find_readme(self.dir)
        p, sddist.metadata.description, sddist.metadata.long_description \
            = pyron.readme.inspect_readme(readme_path)

        self.__dict__['sddist'] = sddist # cache value
        return sddist
