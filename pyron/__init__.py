# -*- coding: utf-8 -*-

"""A command-line DRY Python package builder

This package contains the source code to support the ``pyron`` Python
command-line tool for building and installing packages.

"""
__version__ = '0.1'
__testrunner__ = 'nose'

import _ast, os.path, re, shutil, subprocess, sys
from pprint import pformat

def die(message):
    sys.stderr.write('pyron: ' + message + '\n')
    sys.exit(1)

NAMESPACE_INIT = ("import pkg_resources\n"
                  "pkg_resources.declare_namespace(__name__)\n")
INITS = set(('__init__.py', '__init__.pyc'))

join = os.path.join

class NamespaceStack(object):
    """A NamespaceStack.

    >>> n = NamespaceStack('/a/b', 'c.d.e')
    >>> n.dirs
    ['/a/b/c', '/a/b/c/d']
    >>> n.inits
    ['/a/b/c/__init__.py', '/a/b/c/d/__init__.py']
    >>> n.symlink
    ['/a/b/c/d/e']
    >>> n.linkdest
    ['../../..']

    """

    def __init__(self, base, package_names):
        self.base = base
        n = len(package_names)
        levels = range(1, n)
        self.dirs = [ join(*[base] + package_names[:i]) for i in levels ]
        self.inits = [ join(d, '__init__.py') for d in self.dirs ]
        self.symlink = join(*[base] + package_names)
        self.linkdest = join(*['..'] * n)

    def check(self):
        """Return whether this namespace stack is correct."""
        def content(p):
            f = open(p)
            c = f.read()
            f.close()
            return c

        return (
            all( os.path.isdir(d) for d in self.dirs ) and
            all( len(set(os.listdir(d)) - INITS) == 1
                 for d in self.dirs ) and
            all( os.path.isfile(i) for i in self.inits ) and
            all( content(i) == NAMESPACE_INIT for i in self.inits ) and
            os.path.islink(self.symlink) and
            os.readlink(self.symlink) == self.linkdest
            )

    def build(self):
        """Build this namespace stack."""
        def writeout(p, s):
            f = open(p, 'w')
            f.write(s)
            f.close()

        base = self.dirs[0] if self.dirs else self.symlink
        if os.path.exists(base):
            die("PLEASE REMOVE " + base) #shutil.rmtree(base)
        for d in self.dirs:
            os.mkdir(d) 
        for i in self.inits:
            writeout(i, NAMESPACE_INIT) 
        os.symlink(self.linkdest, self.symlink)

README_NAMES = ('README', 'README.txt')

def find_readme(directory):
    """Find under which name a project keeps its README file."""
    candidates = [ join(directory, name) for name in README_NAMES ]
    candidates = filter(os.path.isfile, candidates)
    if not candidates:
        die('your project must include either %s'
            % ' or '.join(README_NAMES))
    if len(candidates) > 1:
        die('your project cannot supply both %s'
            % ' and '.join(candidates))
    return candidates[0]

title_match = re.compile(ur'``([A-Za-z_.]+)``\W+(.*)').match

def inspect_readme(path, info):
    """Look in a README file for a package name and description."""
    try:
        f = open(path, 'U')
        lines = f.readlines()
        f.close()
    except IOError, e:
        die('cannot read your %s file: %s' % (path, e.strerror))

    try:
        for i in range(len(lines)):
            lines[i] = lines[i].decode('utf-8')
    except IOError: # placeholder until I test this error
        raise

    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1 # skip blank lines
    if i + 1 < len(lines):
        title = lines[i].strip()
        underline = lines[i+1].strip()
        match = title_match(title)
        if (match and underline == underline[0] * len(underline)):
            package_name, description = match.groups()
            if all(package_name.split(u'.')):
                body = u''.join(lines[i+2:]).lstrip(u'\n')
                return body, package_name, description

    die('the beginning of your %s must look like'
        ' (with your choice of punctuation):\n\n'
        '``package`` -- description\n'
        '==========================\n' % path)

def parse(init_path):
    f = open(init_path)
    code = f.read()
    f.close()

    a = compile(code, init_path, 'exec', _ast.PyCF_ONLY_AST)

    if (not a.body or
        not isinstance(a.body[0], _ast.Expr) or
        not isinstance(a.body[0].value, _ast.Str)):
        die('your module has no docstring')

    docstring = a.body[0].value.s
    values = {}

    for a2 in a.body:
        if isinstance(a2, _ast.Assign) and isinstance(a2.value, _ast.Str):
            for target in a2.targets:
                if isinstance(target, _ast.Name):
                    values[target.id] = a2.value.s

    for name in '__version__', '__testrunner__':
        if name not in values:
            die('your module does not define %r at the top level' % name)

    return docstring, values

def main():
    base = '.' # TODO: allow command line to specify
    info = {} # will be filled in as we process files

    # Determine whether the two that we require are present.

    readme_path = find_readme(base)
    body, package_name, description = inspect_readme(readme_path, info)

    init_path = os.path.join(base, '__init__.py')
    docstring, values = parse(init_path)

    package_names = package_name.split('.')
    namespace_packages = [ '.'.join(package_names[:i])
                           for i in range(1, len(package_names)) ]

    setup_args = dict(
        name = package_name,
        version = values['__version__'],
        packages = [ package_name ],
        namespace_packages = namespace_packages,
        zip_safe = False,
        )

    try:
        setup_args['description'] = description.encode('ascii'),
    except UnicodeEncodeError:
        die('your README title must consist of only ASCII characters')

    try:
        setup_args['long_description'] = body.encode('ascii')
    except UnicodeEncodeError:
        die('your README body must consist of only ASCII characters ')

    dotdir = join(base, '.pyron')

    if not os.path.exists(dotdir):
        os.system('virtualenv ' + dotdir)

    # Next, create a tree of parent namespace packages.  If already
    # present, then verify that it is correct; if verification fails,
    # then rebuild it.

    namespace_stack = NamespaceStack(dotdir, package_names)
    if not namespace_stack.check():
        namespace_stack.build()

    python = os.path.join('bin', 'python')

    f = open(join(dotdir, 'setup.py'), 'w')
    f.write('import setuptools\nsetuptools.setup(**\n%s\n)\n'
            % pformat(setup_args))
    f.close()

    subprocess.check_call([ python, 'setup.py', '-q', 'clean', 'develop' ],
                          cwd=dotdir)

    if len(sys.argv) > 1 and sys.argv[1] == 'python':
        os.execvp(python, [ python ] + sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.execvp(python, [ python ] + sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] in ['register']:
        subprocess.check_call([
                python, 'setup.py', '-q', sys.argv[1],
                ], cwd=dotdir)
    elif len(sys.argv) > 1 and sys.argv[1] in ['sdist', 'bdist_egg']:
        subprocess.check_call([
                python, 'setup.py', '-q', sys.argv[1],
                ], cwd=dotdir)
        for name in os.listdir(join(dotdir, 'dist')):
            shutil.move(join(dotdir, 'dist', name), base)
