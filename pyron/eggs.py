"""Routine for creating eggs, without creating intermediate files."""

import pkg_resources
from StringIO import StringIO
from zipfile import ZipFile, ZipInfo

def create_egg(package_name):
    f = StringIO()
    z = ZipFile(f, 'w')
    #z.writestr('EGG-INFO/PKG-INFO', 'foo')

    # Look for periods in the package name to figure out if it is
    # located inside of any namespace packages, and after reducing the
    # name to its top-level component save that as metadata too.

    parent = package_name
    namespace_packages = ''
    while '.' in parent:
        parent = parent.rsplit('.', 1)[0]
        namespace_packages += parent + '\n'
    if namespace_packages:
        z.writestr('EGG-INFO/namespace_packages.txt', namespace_packages)
    z.writestr('EGG-INFO/top_level.txt', parent + '\n')

    # Enforce best practices by refusing to write zip-safe eggs. :-)

    z.writestr('EGG-INFO/not-zip-safe', '\n')

    # Finish writing the zipfile data.

    z.close()
    return f.getvalue()

def write_egg(name, version, version_info, egg_data):
    filename = '{0}-{1}-py{2[0]}.{2[1]}.egg'.format(
        pkg_resources.to_filename(pkg_resources.safe_name(name)),
        pkg_resources.to_filename(pkg_resources.safe_version(version)),
        version_info)
    open(filename, 'w').write(egg_data)
