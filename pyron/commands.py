"""The Pyron command-line tool."""
import os
import sys
import pyron.config
import pyron.dist
from pyron import install

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

def cmd_add(paths):
    for path in paths:
        path = normalize_project_path(path)
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
    project_paths = install.pth_load()
    binpath = install.bin_path()
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
