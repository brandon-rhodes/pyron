"""Routines for building tar.gz source distributions."""

import os
import tarfile
import time
from StringIO import StringIO

this_dir = os.path.dirname(__file__)
namespace_init_path = os.path.join(this_dir, 'namespace_init.py.txt')

NAMESPACE_INIT_PY = """\
# This is a Python "namespace package" http://www.python.org/dev/peps/pep-0382/
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)
"""

SETUP_PY = """\
# This setup.py was generated automatically by Pyron.
# For details, see http://pypi.python.org/pypi/pyron/

from setuptools import setup, find_packages

setup(
    name = %r,
    version = %r,
    description = %r,
    long_description = %r,
    author = %r,
    author_email = %r,
    url = %r,
    classifiers = %r,

    package_dir = {'': 'src'},
    packages = find_packages('src'),
    include_package_data = True,
    install_requires = %r,
    entry_points = %r,
    )
"""

def setup_py_text(project):
    """Return the text of a ``setup.py`` file for `project`."""
    p, description, long_description = project.read_readme()
    project.parse_author()
    project.parse_url()
    return SETUP_PY % (
        project.name, project.version, description, long_description,
        project.author, project.author_email,
        project.url, project.classifiers,
        project.requirements, project.read_entry_points() or '')

def package_dir(name):
    """Return the tarfile directory name for a given package."""
    return '/'.join(name.split('.'))

def tar_add(tar, pathparts, text, mtime):
    """Add a plain-text file to archive `tar`.

    `pathparts` - A list of pathname components like ['foo-0.1', 'setup.py'].
    `text` - The desired textual content of the file.
    `mtime` - The modification time that should be recorded for the file.

    """
    name = '/'.join(pathparts)
    tarinfo = tarfile.TarInfo(name)
    tarinfo.size = len(text)
    tarinfo.mtime = mtime
    tarinfo.mode = 0644
    tarinfo.type = tarfile.REGTYPE
    tarinfo.uid = 65534  # "nobody" on Ubuntu, for what it's worth
    tarinfo.gid = 65534
    tarinfo.uname = 'nobody'
    tarinfo.gname = 'nobody'
    tar.addfile(tarinfo, StringIO(text))

def write_sdist(project, outfile):
    """Write a gzipped tarfile sdist for `project` to `outfile`."""

    tar = tarfile.open(mode='w:gz', fileobj=outfile)
    now = time.time()
    base = '%s-%s' % (project.name, project.version)
    src = [ base, 'src' ]

    # Build the __init__.py files for any namespace packages.

    for np in project.namespace_packages:
        pathparts = src + np.split('.') + [ '__init__.py' ]
        tar_add(tar, pathparts, NAMESPACE_INIT_PY, now)

    # Copy source code, and any other files, from the project.

    pkgdir = tuple(src + project.name.split('.'))
    for abspath, relpath in project.find_files():
        f = open(abspath, 'rb')
        text = f.read()
        f.close()
        pathparts = pkgdir + os.path.split(relpath)
        tar_add(tar, pathparts, text, now)

    # Finally, add a setup.py file and a MANIFEST.in file.

    text = setup_py_text(project)
    tar_add(tar, [ base, 'setup.py' ], text, now)
    tar_add(tar, [ base, 'MANIFEST.in'], 'recursive-include src *\n', now)

    tar.close()

def save_sdist(project, dirpath):
    """Create a correctly named .tar.gz file and save the sdist into it."""
    filename = '%s-%s.tar.gz' % (project.name, project.version)
    filepath = os.path.join(dirpath, filename)
    outfile = open(filepath, 'w')
    write_sdist(project, outfile)
    outfile.close()
    return filepath
