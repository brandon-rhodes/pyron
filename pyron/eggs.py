"""Routine for creating eggs, without creating intermediate files."""

import os
import pkg_resources
from StringIO import StringIO
from zipfile import ZipFile #, ZipInfo

NAMESPACE_INIT = ('from pkgutil import extend_path\n'
                  '__path__ = extend_path(__path__, __name__)\n')

def append_namespaces(z, namespace_packages):
    """Add namespace package __init__.py files to the zipfile."""
    for name in sorted(namespace_packages):
        z.writestr(name.replace('.', '/') + '/__init__.py', NAMESPACE_INIT)

def zipify(path):
    """Turn `path` into a zip file path, that uses forward slashes."""
    names = os.path.split(path)
    if not names[0]:  # '' indicates that `path` was a simple filename
        return names[1]
    return '/'.join(names)

def append_files(z, project, zipdir):
    """Append to the zipfile any files found in the given directory."""
    for abspath, relpath in project.find_files():
        zippath = zipdir + '/' + zipify(relpath)
        f = open(abspath)
        z.writestr(zippath, f.read())
        f.close()

def create_egg(project):
    """Return a string containing a zipped egg for the given package."""

    f = StringIO()
    z = ZipFile(f, 'w')

    # Look for periods in the package name to figure out if it is
    # located inside of any namespace packages, and after reducing the
    # name to its top-level component save that as metadata too.

    if project.namespace_packages:
        z.writestr(
            'EGG-INFO/namespace_packages.txt',
            ''.join(name + '\n' for name in project.namespace_packages),
            )

    z.writestr('EGG-INFO/top_level.txt', project.top_level + '\n')

    if project.requirements:
        z.writestr('EGG-INFO/requires.txt', '\n'.join(project.requirements))

    entry_points = project.read_entry_points()
    if entry_points is not None:
        z.writestr('EGG-INFO/entry_points.txt', entry_points)

    # Enforce best practices by refusing to write zip-safe eggs. :-)

    z.writestr('EGG-INFO/not-zip-safe', '\n')

    # Now that we are done with the metadata, save the actual data.

    append_namespaces(z, project.namespace_packages)
    append_files(z, project, project.name.replace('.', '/'))

    # Finish writing the zipfile data.

    z.close()
    return f.getvalue()

def write_egg(project, version_info, egg_data, destdir='.'):
    """Write an egg file, formatting its name per the egg specifications."""

    filename = '{0}-{1}-py{2[0]}.{2[1]}.egg'.format(
        pkg_resources.to_filename(pkg_resources.safe_name(project.name)),
        pkg_resources.to_filename(pkg_resources.safe_version(project.version)),
        version_info)
    f = open(os.path.join(destdir, filename), 'w')
    try:
        f.write(egg_data)
    finally:
        f.close()
    return filename
