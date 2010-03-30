"""The Pyron command-line tool."""
import os
import sys
from pyron import pth

def die(message, exitcode=1):
    """Print the `message` to standard error and exit."""
    sys.stdout.write(message)
    sys.stdout.write('\n')
    exit(exitcode)

def expand_ini_path(path):
    """Return the path to the ``.ini`` file at or beneath `path`.

    If `path` already ends with an ``.ini`` filename, then `path` itself
    is returned.  Otherwise, `path` is assumed to be the name of a
    directory, and the return value is `path` plus ``/pyron.ini``.

    """
    p = os.path.abspath(path)
    b = os.path.basename(p)
    if len(b) < 5 or not b.lower().endswith('.ini'):
        p = os.path.join(p, 'pyron.ini')
    return p

def cmd_add(paths):
    paths = [ expand_ini_path(p) for p in paths ]
    pth.add(paths)

def cmd_list():
    inis = pth.pth_load()
    for ini in inis:
        print ini

def cmd_remove(things):
    pass

def main():
    command = sys.argv[1]
    args = sys.argv[2:]
    if command == 'add':
        cmd_add(args)
    elif command == 'list':
        cmd_list()
    elif command in ['remove', 'rm']:
        cmd_remove(args)
