"""pyzen: The DRY Python package tool

The ``pyzen`` command is designed to eliminate the vast reptition that
characterizes the ``setup.py`` file of typical Python packages.  Instead
of needing a setup file, ``pyzen`` simply inspects your package to
gather all of the information it needs to build, test, and distribute.
And thanks to the fact that ``pyzen`` uses the ``distutils`` for source
distributions and the ``setuptools`` for building eggs, the resulting
package should be compatible with everything else in Python.

"""
__version__ = '0.1'
__testrunner__ = 'nose'

def main():
    pass
