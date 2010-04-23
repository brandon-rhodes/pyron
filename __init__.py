# -*- coding: utf-8 -*-

"""A command-line DRY Python package builder

This package contains the source code to support the ``pyron`` Python
command-line tool for building and installing packages.

"""
from __future__ import absolute_import

__version__ = '0.2'
__testrunner__ = 'nose'
__author__ = 'Brandon Craig Rhodes <brandon@rhodesmill.org>'
__url__ = 'http://bitbucket.org/brandon/pyron/'

import email.utils, os.path, shutil, subprocess, sys
from ConfigParser import RawConfigParser
from distutils.command.register import register as RegisterCommand
from distutils.dist import Distribution
from optparse import OptionParser

from .eggs import create_egg, write_egg
from .introspect import parse_project_init
from .readme import find_readme, inspect_readme

def die(message):
    sys.stderr.write('pyron: ' + message + '\n')
    sys.exit(1)

join = os.path.join

usage = """\
usage: %prog build     - build the project in the current directory
       %prog python    - run an interpreter with this project in its PATH
       %prog run <cmd> - run one of your project console entry-points
       %prog register  - upload project metadata to PyPI
       %prog sdist     - generate a .tar.gz ready for distribution
       %prog bdist_egg - generate a binary egg for distribution"""

cmds = ['build', 'egg', 'python', 'run', 'register', 'sdist', 'bdist_egg']

def main():
    """The pyron command line."""
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()

    if not args or args[0] not in cmds:
        parser.print_help()
        sys.exit(1)

    cmd = args[0]
    del args[0]

    base = os.path.abspath('.') # TODO: allow command line to specify

    # Use a distutils "Distribution" object to store package metadata.

    dist = Distribution()
    metadata = dist.metadata

    # Open our ini file.

    ini = RawConfigParser()
    ini.readfp(open('pyron.ini'))
    metadata.url = ini.get('package', 'url')

    # Look at the package being developed with Pyron, and introspect all
    # of the essential facts about it.

    readme_path = find_readme(base)
    metadata.name, metadata.description, metadata.long_description \
        = inspect_readme(readme_path)

    init_path = join(base, '__init__.py')
    values = parse_project_init(init_path)
    metadata.version = values['__version__']
    __author__ = values['__author__']
    metadata.author, metadata.author_email = email.utils.parseaddr(__author__)
    if not metadata.author:
        die('the __author__ defined in your __init__.py must include both'
            ' a name and an email address, like "Ed <ed@example.com>"')

    # Make it possible for the package under development to be imported,
    # without making the user create its namespace packages by hand.

    loader = PyronLoader(metadata.name, base, init_path)
    finder = PyronFinder({ metadata.name: loader })
    sys.meta_path.append(finder)

    if '__requires__' in values:
        # TODO: make sure it's a list
        requires = values['__requires__']
    else:
        requires = []

    facts = {}

    if '__url__' in values:
        metadata.url = values['__url__']

    #facts = scan_package(package_name, base, dotdir)

    if 'console_scripts' in facts and facts['console_scripts']:
        setup_args['entry_points'] = {
            'console_scripts': facts['console_scripts'],
            }

    if os.path.exists('entry_points.ini'):
        f = open('entry_points.ini')
        setup_args['entry_points'] = f.read()
        f.close()

    if cmd == 'build':
        pass # work has already been done, above
    elif cmd == 'egg':
        egg_data = create_egg(package_name, base)
        write_egg(package_name, values['__version__'],
                  sys.version_info, egg_data)
        #agtl-0.4.2-py2.6.egg
    elif cmd == 'python':
        os.execvp(python, [ python ] + sys.argv[2:])
    elif cmd == 'run':
        cmd = join(dotdir, 'bin', sys.argv[2])
        os.execvp(cmd, [ cmd ] + sys.argv[3:])
    #elif cmd == 'test':
    #    os.execvp(python, [ python ] + sys.argv[2:])
    elif cmd == 'register':
        cmd = RegisterCommand(dist)
        cmd.run()
        #subprocess.check_call([
        #        join('bin', 'python'), 'setup.py', '-q', sys.argv[1],
        #        ], cwd=dotdir)
    elif cmd in ['sdist', 'bdist_egg']:
        subprocess.check_call([
                join('bin', 'python'), 'setup.py', '-q'] + sys.argv[1:],
                              cwd=dotdir)
        for name in os.listdir(join(dotdir, 'dist')):
            shutil.move(join(dotdir, 'dist', name), base)
