
``pyron`` -- The DRY Python package builder
===========================================

The ``pyron`` command is designed to eliminate the vast reptition that
characterizes the ``setup.py`` file of typical Python packages.  Instead
of needing a setup file, ``pyron`` simply inspects your package to
gather all of the information it needs to build, test, and distribute.
And thanks to the fact that ``pyron`` uses the ``distutils`` for source
distributions and the ``setuptools`` for building eggs, the resulting
package should be compatible with everything else in Python.
