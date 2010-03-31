"""The Pyron command-line tool."""
import argparse
import os
import sys

import pyron.config
import pyron.dist
import pyron.install

def complain(message):
    """Print the error `message` to standard error."""
    sys.stdout.write('Error: %s\n' % (message,))
    sys.stdout.flush()

def die(message, exitcode=1):
    """Print the error `message` to standard error and exit."""
    complain(message)
    exit(exitcode)

def normalize_project_path(path):
    """Return a project directory, even if its ``pyron.ini`` is supplied.

    The `path` can be relative or absolute, but the return value will
    always be an absolute path.  The `path` can either refer to the
    project directory itself, or to the ``pyron.ini`` file inside.

    """
    a = os.path.abspath(path)
    b = os.path.basename(a)
    if b == 'pyron.ini':
        return os.path.dirname(a)
    else:
        return a

def cmd_add(args):
    paths = args.project
    for path in paths:
        path = normalize_project_path(path)
        dist = pyron.dist.make_distribution(path)
        pyron.install.add(dist)

def cmd_remove(args):
    things = args.project
    project_paths = pyron.install.pth_load()
    dists = [ pyron.dist.make_distribution(p) for p in project_paths ]
    for thing in things:
        for dist in dists:
            if (dist.project_name == thing
                or dist.location == normalize_project_path(thing)):
                pyron.install.remove(dist)
                break
        else:
            complain('not installed: %s' % (thing,))

def cmd_status(arg):
    project_paths = pyron.install.pth_load()
    binpath = pyron.install.bin_path()
    for project_path in project_paths:
        print project_path
        dist = pyron.dist.make_distribution(project_path)
        print '    Package:', dist.project_name
        script_list = sorted(dist.get_entry_map('console_scripts').items())
        for name, entry in script_list:
            print '    Console-script: %s (%s:%s)' % (
                name, entry.module_name, '.'.join(entry.attrs))
            script_path = os.path.join(binpath, name)
            if not os.path.exists(script_path):
                print '        ERROR: SCRIPT MISSING'
        print

def main():
    parser = argparse.ArgumentParser(prog='pyron')
    subparsers = parser.add_subparsers(title='Supported commands')
    sap = subparsers.add_parser

    p = sap('add', help='add a project to active development')
    p.add_argument('project', nargs='+', help='path to a Pyron project')
    p.set_defaults(func=cmd_add)

    p = sap('remove', help='remove a project from development')
    p.add_argument('project', nargs='+', help='path to a Pyron project')
    p.set_defaults(func=cmd_remove)

    p = sap('status', help='list the currently active projects')
    p.set_defaults(func=cmd_status)

    # Rename ugly "optional arguments" titles.

    for p in [ parser ] + subparsers.choices.values():
        p._optionals.title = 'Options'

    # Provide convenient abbreviations.

    subparsers.choices['st'] = subparsers.choices['status']
    subparsers.choices['rm'] = subparsers.choices['remove']

    args = parser.parse_args()
    return args.func(args)
