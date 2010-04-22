# Ironically, this first version of pyron of course needs a setup.py.
# This will be removed once pyron is capable enough to introspect itself.

from setuptools import setup

setup(name = 'pyron',
      version = '0.2',
      description = 'The DRY Python package tool',
      license = 'GPL',
      author = 'Brandon Craig Rhodes',
      author_email = 'brandon@rhodesmill.org',
      url = 'http://bitbucket.org/brandon/pyron/',
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        ],
      packages = [ 'pyron' ],
      install_requires = [ 'argparse' ],
      entry_points = {
        'console_scripts': [ 'pyron = pyron.command:main', ],
        }
      )
