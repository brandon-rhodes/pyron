# Ironically, this first version of pyzen of course needs a setup.py.
# This will be removed once pyzen is capable enough to introspect itself.

from setuptools import setup

setup(name = 'pyzen',
      version = '0.1',
      description = 'The DRY Python package tool',
      license = 'GPL',
      author = 'Brandon Craig Rhodes',
      author_email = 'brandon@rhodesmill.org',
      classifiers = [
        ],
      packages = [ 'pyzen' ],
      entry_points = {
        'console_scripts': [ 'pyzen = pyzen:main', ],
        }
      )
