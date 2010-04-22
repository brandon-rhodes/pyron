"""Test suites for the Pyron package."""

import shutil
import os
import unittest
import tempfile

import pyron.command
from pyron.exceptions import PyronError

class SampleProject(object):
    """Routines for creating a sample Pyron project in a temp directory."""

    def create_project(self):
        self.projectdir = tempfile.mkdtemp(prefix='pyron', suffix='test')
        self.pyron_ini_path = os.path.join(self.projectdir, 'pyron.ini')
        self.pyron_init_py_path = os.path.join(self.projectdir, '__init__.py')

    def delete_project(self):
        shutil.rmtree(self.projectdir)

    def pyron_ini(self, text):
        """Write a pyron.ini file to the project directory."""
        f = open(self.pyron_ini_path, 'w')
        f.write(text)
        f.close()

    def init_py(self, text):
        """Write an __init__.py file to the project directory."""
        f = open(self.pyron_init_py_path, 'w')
        f.write(text)
        f.close()

    def pyron(self, *args):
        args = list(args)
        args.append(self.projectdir)
        pyron.command.run(args)

    def assertError(self, pattern, *args):
        try:
            self.pyron(*args)
        except PyronError, e:
            if pattern not in str(e):
                raise RuntimeError(
                    'running "pyron %s" successfully caused an error,'
                    ' but the text of the message does not contain the'
                    ' pattern %r: %r' % (' '.join(args), pattern, str(e)))
        else:
            raise RuntimeError(
                'running Pyron with the arguments %r failed to make it die'
                % (' '.join(args),))

#
# The tests themselves.
#

class TestErrorMessages(unittest.TestCase, SampleProject):

    def setUp(self):
        self.create_project()

    def tearDown(self):
        self.delete_project()

    def test_missing_pyron_ini(self):
        self.assertError('cannot open file', 'upload')

    def test_unreadable_pyron_ini(self):
        self.pyron_ini('foo = bar\n')
        self.init_py('__version__ = "0.1"')
        os.chmod(self.pyron_ini_path, 0x000)
        self.assertError('cannot open file', 'upload')
        os.chmod(self.pyron_ini_path, 0x600)

    def test_sectionless_pyron_ini(self):
        self.pyron_ini('foo = bar\n')
        self.init_py('__version__ = "0.1"')
        self.assertError('pyron.ini has no section named [package]', 'upload')

    def test_missing_init_py(self):
        self.pyron_ini('[package]\nname = foo\n')
        self.assertError('__init__.py: No such file or directory', 'upload')

if __name__ == '__main__':
    unittest.main()
