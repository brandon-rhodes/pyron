# Ironically, this first version of pyron of course needs a setup.py.
# This will be removed once pyron is capable enough to introspect itself.

from setuptools import setup

setup(name = 'pyron',
      version = '0.1',
      description = 'The DRY Python package tool',
      license = 'GPL',
      author = 'Brandon Craig Rhodes',
      author_email = 'brandon@rhodesmill.org',
      classifiers = [
        ],
      packages = [ 'pyron' ],
      entry_points = {
        'console_scripts': [ 'pyron = pyron:main', ],
        }
      )
