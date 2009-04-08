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

import os.path, parser, sys
from pyzen.parse import get_docstring

def die(message):
    sys.stderr.write(message + '\n')
    sys.exit(1)

def main():
    directory = os.getcwd() # TODO: allow command line to specify
    init_path = os.path.join(directory, '__init__.py')
    init = open(init_path).read()
    suite = parser.suite(init)
    code = suite.compile()
    tup = suite.totuple()
    successful, results = get_docstring(tup)
    if not successful:
        die('Error: no module docstring in %s' % (init_path))
    docstring_expr = results['docstring']
    docstring = eval(docstring_expr) # since it has quotes around it
    first_line = docstring.strip().split('\n')[0].strip()
    if not first_line:
        die('Error: first line of docstring is blank in %s' % (init_path))
    pieces = first_line.split(':', 1)
    if len(pieces) != 2:
        die('Error: first line of docstring is not a module name followed by a colon and a description in %s' % (init_path))
    module_name, description = pieces
    
