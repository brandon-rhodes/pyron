# -*- coding: utf-8 -*-

"""A command-line DRY Python package builder

This package contains the source code to support the ``pyron`` Python
command-line tool for building and installing packages.

"""
from __future__ import absolute_import

__version__ = '0.1'
__testrunner__ = 'nose'

import _ast, email.utils, os.path, shutil, subprocess, sys
from pprint import pformat

from .readme import find_readme, inspect_readme
from .namespaces import NamespaceStack

def die(message):
    sys.stderr.write('pyron: ' + message + '\n')
    sys.exit(1)

join = os.path.join

class ASTNotSimpleConstant(Exception):
    pass

def interpret(node):
    if isinstance(node, _ast.Str):
        return node.s
    elif isinstance(node, _ast.Num):
        return node.n
    elif isinstance(node, _ast.Tuple):
        return tuple( interpret(e) for e in node.elts )
    elif isinstance(node, _ast.List):
        return list( interpret(e) for e in node.elts )
    else:
        raise ASTNotSimpleConstant()

def parse(init_path):
    """Parse a package-wide __init__.py module for information."""
    f = open(init_path)
    code = f.read()
    f.close()

    a = compile(code, init_path, 'exec', _ast.PyCF_ONLY_AST)

    global_constants = {}

    for a2 in a.body:
        if isinstance(a2, _ast.Assign):
            try:
                rhs = interpret(a2.value)
            except ASTNotSimpleConstant:
                continue

            lhs = a2.targets[0] # why is `a2.targets` a list?

            if isinstance(lhs, _ast.Name):
                targets = [ lhs ]
                values = [ rhs ]
            else: # `targets` must be tuple or list lhs
                targets = lhs.elts
                values = rhs

            for target, value in zip(targets, values):
                global_constants[target.id] = value

    for name in '__version__', '__testrunner__', '__author__':
        if name not in global_constants:
            die('your module does not define %r at the top level' % name)

    return global_constants

def main():
    base = '.' # TODO: allow command line to specify

    readme_path = find_readme(base)
    package_name, description, body = inspect_readme(readme_path)

    init_path = join(base, '__init__.py')
    values = parse(init_path)

    __author__ = values['__author__']
    author, author_email = email.utils.parseaddr(__author__)
    if not author:
        die('the __author__ defined in your __init__.py must include both'
            ' a name and an email address, like "Ed <ed@example.com>"')

    package_names = package_name.split('.')
    namespace_packages = [ '.'.join(package_names[:i])
                           for i in range(1, len(package_names)) ]

    if '__requires__' in values:
        # TODO: make sure it's a list
        requires = values['__requires__']
    else:
        requires = []

    setup_args = dict(
        name = package_name,
        version = values['__version__'],
        description = description,
        long_description = body,
        author = author,
        author_email = author_email,
        packages = [ package_name ],
        namespace_packages = namespace_packages,
        zip_safe = False,
        install_requires = requires,
        )

    dotdir = join(base, '.pyron')

    if not os.path.exists(dotdir):
        os.system('virtualenv ' + dotdir)

    # Next, create a tree of parent namespace packages.  If already
    # present, then verify that it is correct; if verification fails,
    # then rebuild it.

    namespace_stack = NamespaceStack(dotdir, package_names)
    if not namespace_stack.check():
        namespace_stack.build()

    python = join(dotdir, 'bin', 'python')
    setup_py = join(dotdir, 'setup.py')

    f = open(setup_py, 'w')
    f.write('import setuptools\nsetuptools.setup(**\n%s\n)\n'
            % pformat(setup_args))
    f.close()

    subprocess.check_call([ join('bin', 'python'), 'setup.py',
                            '-q', 'clean', 'develop' ],
                          cwd=dotdir)

    if len(sys.argv) > 1 and sys.argv[1] == 'python':
        os.execvp(python, [ python ] + sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.execvp(python, [ python ] + sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] in ['register']:
        subprocess.check_call([
                join('bin', 'python'), 'setup.py', '-q', sys.argv[1],
                ], cwd=dotdir)
    elif len(sys.argv) > 1 and sys.argv[1] in ['sdist', 'bdist_egg']:
        subprocess.check_call([
                join('bin', 'python'), 'setup.py', '-q', sys.argv[1],
                ], cwd=dotdir)
        for name in os.listdir(join(dotdir, 'dist')):
            shutil.move(join(dotdir, 'dist', name), base)
