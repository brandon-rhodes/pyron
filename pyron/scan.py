"""Routines used by pyron to scan packages and modules."""

import os, pyclbr, re

join = os.path.join
id_match = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$').match

def scan_module(module_name, pathdir, facts):
    contents = pyclbr.readmodule_ex(module_name, path=[ pathdir ])
    for name in contents:
        if name.startswith('console_script_') and len(name) > 15:
            script_name = name[15:]
            declaration = '%s = %s:%s' % (script_name, module_name, name)
            facts['console_scripts'].append(declaration)

def scan_package(package_name, directory, pathdir, facts=None):
    """Return facts about the package named `name` under `directory`."""

    # If we are just starting a recursive scan, then start with a blank
    # slate of facts.

    if facts is None:
        facts = {'console_scripts': []}

    # Ignore this directory if it lacks an __init__.py.

    listing = os.listdir(directory)
    if '__init__.py' not in listing:
        return

    # Otherwise, process the files and sub-directories whose names could
    # be legal Python package names.

    for filename in listing:
        if filename.endswith('.py'):
            path = join(directory, filename)
            bare_filename = filename[:-3]
            if id_match(bare_filename) and os.path.isfile(path):
                if bare_filename == '__init__':
                    scan_module(package_name, pathdir, facts)
                else:
                    module_name = '.'.join((package_name, bare_filename))
                    scan_module(module_name, pathdir, facts)
        else:
            path = join(directory, filename)
            if id_match(filename) and os.path.isdir(path):
                subpackage_name = '.'.join((package_name, filename))
                scan_package(subpackage_name, path, pathdir, facts)

    # Return everything we have found.

    return facts
