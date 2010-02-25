"""Routine for writing egg files."""

from zipfile import ZipFile, ZipInfo
from StringIO import StringIO

def create_egg():
    f = StringIO()
    z = ZipFile(f, 'w')
    z.writestr('EGG-INFO/not-zip-safe', '\n')
    z.close()
    return f.getvalue()
