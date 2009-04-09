"""Routines for examining the README file of a Python project."""

import htmlentitydefs, os.path, re

join = os.path.join

README_NAMES = ('README', 'README.txt')
TITLE_MATCH = re.compile(ur'``([A-Za-z_.]+)``\W+(.*)').match
DEFMAP = dict( (unichr(k), v) for (k,v)
               in htmlentitydefs.codepoint2name.items() )

def find_readme(directory):
    """Find under which name a project keeps its README file."""
    candidates = [ join(directory, name) for name in README_NAMES ]
    candidates = filter(os.path.isfile, candidates)
    if not candidates:
        raise RuntimeError('your project must include either %s'
                           % ' or '.join(README_NAMES))
    if len(candidates) > 1:
        raise RuntimeError('your project cannot supply both %s'
                           % ' and '.join(candidates))
    return candidates[0]

def inspect_readme(path):
    """Look in a README file for a package name and description."""
    try:
        f = open(path, 'U')
        readme = f.read()
        f.close()
    except IOError, e:
        raise RuntimeError('cannot read your %s file: %s'
                           % (path, e.strerror))

    try:
        readme = readme.decode('ascii')
    except UnicodeDecodeError:
        raise RuntimeError(
            'because of the limitations of setuptools and the Python'
            ' Package Index, your %s file must contain Restructured Text'
            ' consisting only of ASCII characters' % path)

    format_error = RuntimeError(
        'the beginning of your %s must look like (with your choice of'
        ' punctuation):\n\n``package`` -- description\n'
        '==========================\n' % path)

    # Skip any initial blank lines, until we have a non-blank line
    # caught in [i0:i1].

    i1 = -1
    line = None
    while not line:
        i0 = i1 + 1
        i1 = readme.index('\n', i0)
        if i1 == -1:
            raise format_error
        line = readme[i0:i1].strip()

    # Take that first non-blank line and the one that follows.

    title = line
    i2 = readme.index('\n', i1 + 1)
    if i2 == -1:
        raise format_error
    underline = readme[i1+1:i2].strip()
    body = readme[i2+1:].lstrip('\n')

    # Parse the package name and description from the title, and return.

    match = TITLE_MATCH(title)
    if (match and underline == underline[0] * len(underline)):
        package_name, description = match.groups()
        if all(package_name.split(u'.')):
            return package_name, description, body

    raise format_error
