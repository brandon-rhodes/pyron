"""Routines for reading ``pyron.ini`` configuration files."""

from ConfigParser import RawConfigParser, NoOptionError

def read(config_path):
    """Read the ``pyron.ini`` file at the given path."""
    config = RawConfigParser()
    try:
        f = open(config_path)
        config.readfp(f)
    except IOError:
        raise RuntimeError('cannot read file: %s' % (config_path,))
    try:
        name = config.get('package', 'name')
    except NoOptionError:
        raise RuntimeError('missing "name" in [package] section: %s'
                           % (config_path,))
    print name
