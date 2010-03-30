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
    return dist
