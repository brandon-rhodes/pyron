"""Routine for creating eggs, without creating intermediate files."""

import pkg_resources
from StringIO import StringIO
from zipfile import ZipFile, ZipInfo

def create_egg():
    f = StringIO()
    z = ZipFile(f, 'w')
    #z.writestr('EGG-INFO/PKG-INFO', 'foo')
    z.writestr('EGG-INFO/not-zip-safe', '\n')  # enforce "best practices" :-)
    z.close()
    return f.getvalue()

def write_egg(name, version, version_info, egg_data):
    filename = '{0}-{1}-py{2[0]}.{2[1]}.egg'.format(
        pkg_resources.to_filename(pkg_resources.safe_name(name)),
        pkg_resources.to_filename(pkg_resources.safe_version(version)),
        version_info)
    open(filename, 'w').write(egg_data)
