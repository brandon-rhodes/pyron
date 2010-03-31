"""Routines for building a setuptools ``Distribution`` object."""

import os
import pkg_resources

import pyron.config
import pyron.introspect

def make_distribution(project_dir):
    """Return a Distribution giving information about a Pyron project."""

    pyron_ini_path = os.path.join(project_dir, 'pyron.ini')
    init_path = os.path.join(project_dir, '__init__.py')
    entry_points_path = os.path.join(project_dir, 'entry_points.ini')

    config = pyron.config.read_pyron_ini(pyron_ini_path)
    global_constants = pyron.introspect.parse_project_init(init_path)

    dist = pkg_resources.Distribution(
        project_name=config.get('package', 'name'),
        version=global_constants['__version__'],
        location=project_dir,
        )

    if os.path.exists(entry_points_path):
        pyron.config.read_entry_points_ini(entry_points_path, dist)

    # Add some unauthorized attributes for our own later use.

    dist.init_path = init_path
    # TODO: add things like url and description

    return dist
