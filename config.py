"""Routines for reading various configuration files."""

from ConfigParser import RawConfigParser, MissingSectionHeaderError
from pyron.exceptions import PyronError

def read_pyron_ini(path):
    """Read a project's ``pyron.ini``, returning a ConfigParser."""
    try:
        f = open(path)
    except IOError:
        raise PyronError('cannot open file: %s' % (path,))

    config = RawConfigParser()
    try:
        config.readfp(f)
    except IOError:
        raise PyronError('cannot read file: %s' % (path,))
    except MissingSectionHeaderError:
        raise PyronError('%s has no section named [package]' % (path,))
    finally:
        f.close()

    return config
