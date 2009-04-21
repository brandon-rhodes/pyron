# -*- coding: utf-8 -*-

"""A command-line DRY Python package builder

This package contains the source code to support the ``pyron`` Python
command-line tool for building and installing packages.

"""
from __future__ import absolute_import

__version__ = '0.1'
__testrunner__ = 'nose'
__author__ = 'Brandon Craig Rhodes <brandon@rhodesmill.org>'
__url__ = 'http://bitbucket.org/brandon/pyron/'

import email.utils, os.path, shutil, subprocess, sys
from pprint import pformat

from .introspect import parse_project_init
from .readme import find_readme, inspect_readme
from .namespaces import NamespaceStack
from .scan import scan_package

def die(message):
    sys.stderr.write('pyron: ' + message + '\n')
    sys.exit(1)

join = os.path.join

def main():
    base = '.' # TODO: allow command line to specify

    readme_path = find_readme(base)
    package_name, description, body = inspect_readme(readme_path)

    init_path = join(base, '__init__.py')
    values = parse_project_init(init_path)

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

    facts = {}

    setup_args = dict(
        name = package_name,
        version = values['__version__'],
        description = description,
        long_description = body,
        author = author,
        author_email = author_email,
        packages = [ package_name ] + namespace_packages,
        namespace_packages = namespace_packages,
        zip_safe = False,
        install_requires = requires,
        )

    if '__url__' in values:
        setup_args['url'] = values['__url__']

    #

    dotdir = join(base, '.pyron')

    if not os.path.exists(dotdir):
        os.system('virtualenv ' + dotdir)

    # Next, create a tree of parent namespace packages.  If already
    # present, then verify that it is correct; if verification fails,
    # then rebuild it.

    namespace_stack = NamespaceStack(dotdir, package_names)
    if not namespace_stack.check():
        namespace_stack.build()

    # Now that the namespace stack exists, we can introspect the
    # contents of this package like a real module.

    facts = scan_package(package_name, base, dotdir)

    if 'console_scripts' in facts and facts['console_scripts']:
        setup_args['entry_points'] = {
            'console_scripts': facts['console_scripts'],
            }

    #

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
    elif len(sys.argv) > 1 and sys.argv[1] == 'run':
        cmd = join(dotdir, 'bin', sys.argv[2])
        os.execvp(cmd, [ cmd ] + sys.argv[3:])
    #elif len(sys.argv) > 1 and sys.argv[1] == 'test':
    #    os.execvp(python, [ python ] + sys.argv[2:])
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
