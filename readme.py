"""Routines for examining the README file of a Python project."""

import codecs
import htmlentitydefs
import re
import os

from pyron.exceptions import PyronError

join = os.path.join

README_NAMES = ('README', 'README.txt')
README_MATCH = re.compile(ur'\n+(``[A-Za-z_.]+`` *-- *)?(.*)\n[=-]*\n').match
DEFMAP = dict( (unichr(k), v) for (k,v)
               in htmlentitydefs.codepoint2name.items() )

def find_readme(directory):
    """Find under which name a project keeps its README file."""
    candidates = [ join(directory, name) for name in README_NAMES ]
    candidates = filter(os.path.isfile, candidates)
    if not candidates:
        raise PyronError('your project must include either %s'
                         % ' or '.join(README_NAMES))
    if len(candidates) > 1:
        raise PyronError('your project cannot supply both %s'
                         % ' and '.join(candidates))
    return candidates[0]

def inspect_readme(path):
    """Look in a README file for a package name and description."""
    try:
        f = codecs.open(path, 'U', 'ascii')
    except IOError, e:
        raise PyronError('cannot open %s: %s' % (path, e.strerror))
    try:
        readme = f.read()
    except IOError, e:
        raise PyronError('cannot read %s: %s' % (path, e.strerror))
    except UnicodeDecodeError:
        raise PyronError(
            'because of the limitations of setuptools and the Python'
            ' Package Index, your %s file must contain Restructured Text'
            ' consisting only of ASCII characters' % path)
    finally:
        f.close()

    def format_error():
        return PyronError(
            'the beginning of your %s must look like (the package name can'
            ' omitted):\n\n``package`` -- brief description\n'
            '================================\n\n' % path)

    match = README_MATCH(readme)
    if match:
        package_name = match.group(1)
        description = match.group(2)
        body = readme[match.end():]
        return package_name, description, body

    raise format_error
