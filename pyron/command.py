"""The Pyron command-line tool."""
import argparse
import os
import shutil
import sys
import tempfile
from distutils.command.register import register as RegisterCommand
from distutils.command.upload import upload as UploadCommand

import pyron.config
import pyron.eggs
import pyron.install
import pyron.project
import pyron.sdist
from pyron.exceptions import PyronError

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
        dist = pyron.project.Project(path).prdist
        # WorkingSet.resolv(requirements, installer=?) to download them
        pyron.install.add(dist)

def cmd_egg(args):
    paths = args.project
    for path in paths:
        path = normalize_project_path(path)
        project = pyron.project.Project(path)
        egg_data = pyron.eggs.create_egg(project)
        filename = pyron.eggs.write_egg(project, sys.version_info, egg_data)
        print 'Wrote:', filename

def cmd_register(args):
    paths = args.project
    for path in paths:
        path = normalize_project_path(path)
        project = pyron.project.Project(path)
        sddist = project.sddist
        cmd = RegisterCommand(sddist)
        cmd.run()

def cmd_remove(args):
    things = args.project
    project_paths = pyron.install.pth_load()
    dists = [ pyron.project.Project(p).prdist for p in project_paths ]
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
        dist = pyron.project.Project(project_path).prdist
        print '    Package:', dist.project_name
        script_list = sorted(dist.get_entry_map('console_scripts').items())
        for name, entry in script_list:
            print '    Console-script: %s (%s:%s)' % (
                name, entry.module_name, '.'.join(entry.attrs))
            script_path = os.path.join(binpath, name)
            if not os.path.exists(script_path):
                print '        ERROR: SCRIPT MISSING'
        print

def cmd_upload(args):
    # Drat; the distutils need an actual physical file to upload, so we
    # have to waste time and energy creating one in a temporary directory.
    paths = args.project
    for path in paths:
        path = normalize_project_path(path)
        project = pyron.project.Project(path)
        sddist = project.sddist
        tmpdir = tempfile.mkdtemp(suffix='pyron')
        try:
            print pyron.sdist.save_temporary_sdist(project, tmpdir)
            raw_input()
            return
            cmd = UploadCommand(sddist)
            cmd.initialize_options()
            cmd.finalize_options()
            cmd.distribution.dist_files = [
                ('bdist_egg', sys.version.split()[0], eggpath),
                ]
            cmd.run()
        finally:
            shutil.rmtree(tmpdir)

def run(argv):
    """The Pyron main program logic, which runs with the given `argv`.

    Within both this function and all its subsidiary Pyron functions, a
    PyronError is raised if a failure occurs which needs to be reported
    to the user.

    """
    parser = argparse.ArgumentParser(prog='pyron')
    subparsers = parser.add_subparsers(title='Argument', metavar='COMMAND')
    sap = subparsers.add_parser

    # More commands to add: egg, register

    p = sap('add', help='Add a project to active development')
    p.add_argument('project', default='.', nargs='*',
                   help='Pyron project path (defaults to current directory)')
    p.set_defaults(func=cmd_add)

    p = sap('egg', help='Build an egg for distribution')
    p.add_argument('project', default='.', nargs='+',
                   help='Pyron project path')
    p.set_defaults(func=cmd_egg)

    p = sap('register', help='Register a package with PyPI')
    p.add_argument('project', default='.', nargs='+',
                   help='Pyron project path')
    p.set_defaults(func=cmd_register)

    p = sap('remove', help='Remove a project from active development ("rm")')
    p.add_argument('project', default='.', nargs='*',
                   help='Pyron project path (defaults to current directory)')
    p.set_defaults(func=cmd_remove)

    p = sap('status', help='List the currently active projects ("st")')
    p.set_defaults(func=cmd_status)

    p = sap('upload', help='Upload an egg of your project to PyPI')
    p.add_argument('project', default='.', nargs='*',
                   help='Pyron project path (defaults to current directory)')
    p.set_defaults(func=cmd_upload)

    # Rename ugly "optional arguments" titles.

    for p in [ parser ] + subparsers.choices.values():
        p._optionals.title = 'Options'

    # Provide convenient abbreviations.

    subparsers.choices['st'] = subparsers.choices['status']
    subparsers.choices['rm'] = subparsers.choices['remove']

    args = parser.parse_args(argv)
    return args.func(args)

def main():
    """Run the Pyron main program with the arguments in `sys.argv`.

    If `PyronError` is raised, its message is printed to stderr and we
    then exit with a nonzero error code.

    """
    try:
        run(sys.argv[1:])
    except PyronError, e:
        sys.stdout.write('Error: %s\n' % e)
        sys.stdout.flush()
        exit(e.error_code)
