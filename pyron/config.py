"""Routines for reading various configuration files."""

from ConfigParser import RawConfigParser #, NoOptionError

def read_pyron_ini(path):
    """Read a project's ``pyron.ini``, returning a ConfigParser."""
    try:
        f = open(path)
    except IOError:
        raise RuntimeError('cannot open file: %s' % (path,))

    config = RawConfigParser()
    try:
        config.readfp(f)
    except IOError:
        raise RuntimeError('cannot read file: %s' % (path,))
    finally:
        f.close()

    if not config.has_option('package', 'name'):
        raise RuntimeError('missing "name" in [package] section: %s' % (path,))

    return config
