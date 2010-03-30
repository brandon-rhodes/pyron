"""The Pyron command-line tool."""
import os
import sys
import pyron.config
from pyron import pth

def complain(message):
    """Print the error `message` to standard error."""
    sys.stdout.write('Error: %s\n' % (message,))
    sys.stdout.flush()

def die(message, exitcode=1):
    """Print the error `message` to standard error and exit."""
    complain(message)
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

def cmd_remove(things):
    config_paths = pth.pth_load()
    for thing in things:
        if thing in config_paths:
            config_paths.remove(thing)
        else:
            die('not installed: %s' % (thing,))
    pth.pth_save(config_paths)

def cmd_status():
    config_paths = pth.pth_load()
    for config_path in config_paths:
        print config_path
        dist = pyron.config.read(config_path)
        print "    Package:", dist.metadata.name
        print

def main():
    command = sys.argv[1]
    args = sys.argv[2:]
    try:
        if command == 'add':
            cmd_add(args)
        elif command in ['remove', 'rm']:
            cmd_remove(args)
        elif command in ['status', 'st']:
            cmd_status()
    except RuntimeError, e:
        sys.stderr.write('Error: ')
        sys.stderr.write(str(e))
        sys.stderr.write('\n')
        sys.exit(1)
