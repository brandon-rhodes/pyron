"""The Pyron command-line tool."""
import os
import sys
import pyron.config
from pyron import install

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
    for path in paths:
        path = expand_ini_path(path)
        dist = pyron.config.read(path)
        install.add_scripts(dist)
        install.add([ path ])

def cmd_remove(things):
    config_paths = install.pth_load()
    for thing in things:
        ething = expand_ini_path
        if thing in config_paths:
            config_paths.remove(thing)
            continue
        ething = expand_ini_path(thing)
        if ething in config_paths:
            config_paths.remove(ething)
            continue
        complain('not installed: %s' % (thing,))
    install.pth_save(config_paths)

def cmd_status():
    config_paths = install.pth_load()
    binpath = install.bin_path()
    for config_path in config_paths:
        print config_path
        dist = pyron.config.read(config_path)
        print '    Package:', dist.metadata.name
        if 'console_scripts' in dist.entry_points:
            scripts = sorted(dist.entry_points['console_scripts'].items())
            for script, pyname in scripts:
                print '    Console-script: %s (%s)' % (script, pyname)
                script_path = os.path.join(binpath, script)
                if not os.path.exists(script_path):
                    print '        ERROR: SCRIPT MISSING'
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
