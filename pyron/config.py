"""Routines for reading ``pyron.ini`` configuration files."""

from ConfigParser import RawConfigParser, NoOptionError
from distutils.dist import Distribution

def read(config_path):
    """Read the ``pyron.ini`` file at the given path."""
    dist = Distribution()
    metadata = dist.metadata

    config = RawConfigParser()
    try:
        f = open(config_path)
        config.readfp(f)
    except IOError:
        raise RuntimeError('cannot read file: %s' % (config_path,))
    try:
        metadata.name = config.get('package', 'name')
    except NoOptionError:
        raise RuntimeError('missing "name" in [package] section: %s'
                           % (config_path,))

    metadata.version = '1.1' # TODO change this to grab from __init__.py

    dist.entry_points = {}  # add unauthorized Distribute attribute (gulp!)
    if config.has_section('console_scripts'):
        csdict = dict(config.items('console_scripts'))
        dist.entry_points['console_scripts'] = csdict

    return dist
