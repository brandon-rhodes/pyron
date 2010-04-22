"""Routines for building tar.gz source distributions."""

import os
import tarfile

namespace_init_path = os.path.join(os.path.dirname(__file__),
                                   'namespace_init.py.txt')

def package_dir(name):
    """Return the tarfile directory name for a given package."""
    return '/'.join(name.split('.'))

def write_sdist(project, outfile):
    """Write a gzipped tarfile sdist for `project` to `outfile`."""

    tar = tarfile.open(mode='w:gz', fileobj=outfile)
    base = '%s-%s' % (project.name, project.version)
    src = os.path.join(base, 'src')

    for np in project.namespace_packages:
        dirname = '/'.join([ src, package_dir(np) ])
        tar.add(namespace_init_path, '/'.join([ dirname, '__init__.py' ]))

    dirname = '/'.join([ src, package_dir(project.name) ])
    for abspath, relpath in project.find_files():
        tar.add(abspath,
                '/'.join([ dirname, relpath ]))
    tar.close()

def save_temporary_sdist(project, tmpdir):
    """Create a temporary .tar.gz file and save a tarfile into it."""
    filename = '%s-%s.tar.gz' % (project.name, project.version)
    filepath = os.path.join(tmpdir, filename)
    outfile = open(filepath, 'w')
    write_sdist(project, outfile)
    outfile.close()
    return filepath
