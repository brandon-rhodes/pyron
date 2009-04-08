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
    base = os.getcwd() # TODO: allow command line to specify
    init_path = os.path.join(base, '__init__.py')
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
    package_name = pieces[0].strip()
    description = pieces[1].strip()
    setup_args = dict(
        name = package_name,
        description = description,
        packages = [ package_name ],
        package_dir = { package_name: '.' },
        #namespace_packages = [ package_name ],
        #zip_safe = False,
        )
    import pprint
    pprint.pprint(setup_args)
    if not os.path.exists('.pyzen'):
        os.system('virtualenv .pyzen')
    import setuptools
    #old_args = sys.argv[1:]
    #sys.argv[1:] = [
    #    #'clean', '--build-base', '.pyzen',
    #    'install', '--build-base', '.pyzen',
    #    ]
    python = os.path.join(base, '.pyzen', 'bin', 'python')
    dotdir = os.path.join(base, '.pyzen')
    os.chdir(dotdir)
    f = open('setup.py', 'w')
    f.write('import setuptools; setuptools.setup(**%r)' % setup_args)
    f.close()
    os.execl(python, python, 'setup.py',
             'clean', 'build', 'install')
    #setuptools.setup(**args)
    if old_args and old_args[0] == 'python':
        print "go!"
       # os.execvp('python', old_args[1:])
